# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Tests that random processes generate values with expected stats."""

import math
from absl.testing import absltest
from absl.testing import parameterized
import chex
from flax import nnx
import jax
import jax.numpy as jnp
from neuralgcm.experimental.core import coordinates
from neuralgcm.experimental.core import parallelism
from neuralgcm.experimental.core import random_processes
from neuralgcm.experimental.core import spherical_transforms
from neuralgcm.experimental.core import typing
from neuralgcm.experimental.core import units
import numpy as np
import scipy.stats


def _auto_correlation_1d(series):
  centered = series - jnp.mean(series)
  autocov = jax.scipy.signal.correlate(centered, centered, precision='float32')
  autocov = autocov[series.shape[0] - 1 :]
  autocorr = autocov / autocov[0]
  return autocorr


def auto_correlation(series: jax.typing.ArrayLike, axis: int) -> jax.Array:
  """JAX based implementation of tfp.stats.auto_correlation."""
  if series.ndim != 2:
    raise ValueError('series must be 2D')
  i = (axis + 1) % 2  # vectorize along the other axis
  return jax.vmap(_auto_correlation_1d, in_axes=i, out_axes=i)(series)


@absltest.skipThisClass('Base class')
class BaseSphericalHarmonicRandomProcessTest(parameterized.TestCase):
  """Base class for testing variants of random fields on spherical harmonics."""

  def setUp(self):
    super().setUp()
    self.sim_units = units.DEFAULT_UNITS
    self.dt = self.sim_units.nondimensionalize(typing.Quantity('1 hour'))

  def check_correlation_length(
      self,
      samples,
      expected_correlation_length,
      grid,
  ):
    """Checks the correlation length of random field."""
    unused_n_samples, n_lngs, n_lats = samples.shape
    expected_corr_frac = expected_correlation_length / (2 * np.pi * grid.radius)
    # Mean autocorrelation in the lat direction at the longitude=0 line.
    acorr_lat = auto_correlation(samples[:, 0, :], axis=-1).mean(axis=0)
    # There are 2 * n_lats points in the circumference.
    fractional_corr_len_lat = np.argmax(acorr_lat < 0) / (2 * n_lats)
    self.assertBetween(
        fractional_corr_len_lat,
        expected_corr_frac * 0.5,
        expected_corr_frac * 3,
    )
    # Mean autocorrelation in the lng direction at the latitude=0 line.
    acorr_lng = auto_correlation(
        samples[:, :, n_lats // 2],
        axis=-1,
    ).mean(axis=0)
    fractional_corr_len_lng = np.argmax(acorr_lng < 0) / n_lngs
    self.assertBetween(
        fractional_corr_len_lng,
        expected_corr_frac * 0.2,
        expected_corr_frac * 3,
    )

  def check_mean(
      self,
      samples,
      grid,
      expected_mean,
      variance,
      correlation_length,
      mean_tol_in_standard_errs,
  ):
    """Checks the mean (at every point & average) of samples."""
    n_samples, unused_n_lngs, unused_n_lats = samples.shape

    # Pointwise mean should be with tol with high probability everywhere.
    # Since we're testing many (lat/lon) points, we allow for some deviations.
    standard_error = np.sqrt(variance) / np.sqrt(n_samples) if variance else 0.0
    np.testing.assert_allclose(
        # 95% of points are within specified tol. There may be outliers.
        np.percentile(np.mean(samples, axis=0), 95),
        expected_mean,
        atol=mean_tol_in_standard_errs * standard_error,
    )
    np.testing.assert_allclose(
        # 100% of points are within a looser tol.
        np.mean(samples, axis=0),
        expected_mean,
        atol=2 * mean_tol_in_standard_errs * standard_error,
    )

    # Check average mean over whole earth (standard_error will be lower so this
    # is a good second check).
    expected_corr_frac = correlation_length / grid.radius
    n_equivalent_integrated_samples = n_samples / expected_corr_frac**2
    if variance:
      standard_error = np.sqrt(variance) / np.sqrt(
          n_equivalent_integrated_samples
      )
    else:
      standard_error = 0.0
    np.testing.assert_allclose(
        np.mean(samples),
        expected_mean,
        atol=mean_tol_in_standard_errs * standard_error,
    )

  def check_variance(
      self,
      samples,
      ylm_transform,
      correlation_length,
      expected_variance,
      var_tol_in_standard_errs,
  ):
    expected_variance = expected_variance or 0.0
    expected_integrated_variance = (
        expected_variance * 4 * np.pi * ylm_transform.radius**2
    )

    n_samples, unused_n_lngs, unused_n_lats = samples.shape
    # Integrating over the sphere we get additional statistical power since
    # points decorrelate.
    expected_corr_frac = correlation_length / ylm_transform.radius
    n_equivalent_integrated_samples = n_samples / expected_corr_frac**2
    standard_error = np.sqrt(
        # The variance of a (normal) variance estimate is 2 σ⁴ / (n - 1).
        2
        * expected_integrated_variance**2
        / n_equivalent_integrated_samples
    )

    np.testing.assert_allclose(
        ylm_transform.dinosaur_grid.integrate(np.var(samples, axis=0)),
        expected_integrated_variance,
        atol=var_tol_in_standard_errs * standard_error,
        rtol=0.0,
    )

  def check_unconditional_and_trajectory_stats(
      self,
      random_field,
      mean,
      variance,
      ylm_transform,
      correlation_length,
      correlation_time,
      run_mean_check=True,
      run_variance_check=True,
      run_correlation_length_check=True,
      run_correlation_time_check=True,
      mean_tol_in_standard_errs=4,
      var_tol_in_standard_errs=4,
  ):
    dt = self.dt
    grid = ylm_transform.nodal_grid

    # generating multiple trajectories of random fields.
    n_samples = 500
    unroll_length = 40
    init_rngs = jax.random.split(jax.random.key(5), n_samples)
    graph, params = nnx.split(random_field)
    sample_fn = lambda x: graph.apply(params).unconditional_sample(x)[0]
    evaluate_fn = lambda x: graph.apply(params).state_values(grid, x)[0]
    advance_fn = lambda x: graph.apply(params).advance(x)[0]
    batch_sample_fn = jax.vmap(sample_fn)
    batch_evaluate_fn = jax.vmap(evaluate_fn)
    batch_advance_fn = jax.vmap(advance_fn)
    initial_states = batch_sample_fn(init_rngs)
    initial_values = batch_evaluate_fn(initial_states).data

    with self.subTest('unconditional_sample_shape'):
      self.assertEqual(initial_values.shape, (n_samples,) + grid.shape)

    # TODO(dkochkov): Consider adding sizes/size properties to coordinate/field.
    n_lats = grid.fields['latitude'].shape[0]
    n_lngs = grid.fields['longitude'].shape[0]
    self.assertTupleEqual((n_samples, n_lngs, n_lats), initial_values.shape)

    if run_correlation_length_check and variance is not None:
      with self.subTest('unconditional_sample_correlation_len'):
        self.check_correlation_length(initial_values, correlation_length, grid)

    if run_mean_check:
      with self.subTest('unconditional_sample_pointwise_mean'):
        self.check_mean(
            initial_values,
            grid,
            expected_mean=mean,
            variance=variance,
            correlation_length=correlation_length,
            mean_tol_in_standard_errs=mean_tol_in_standard_errs,
        )

    if run_variance_check:
      with self.subTest('unconditional_sample_integrated_var'):
        self.check_variance(
            initial_values,
            ylm_transform,
            correlation_length=correlation_length,
            expected_variance=variance,
            var_tol_in_standard_errs=var_tol_in_standard_errs,
        )

    def step_fn(c, _):
      next_c = batch_advance_fn(c)
      next_output = batch_evaluate_fn(next_c).data
      return (next_c, next_output)

    _, field_trajectory = jax.lax.scan(
        step_fn, initial_states, xs=None, length=unroll_length
    )
    field_trajectory = jax.device_get(field_trajectory)

    if run_correlation_time_check and variance is not None:
      with self.subTest('trajectory_correlation_time'):
        # Mean autocorrelation at the lat=lng=0 point.
        acorr = auto_correlation(
            field_trajectory[:, :, n_lngs // 2, 0], axis=0
        ).mean(axis=1)
        sample_decorr_time = dt * np.argmax(acorr < 0)
        self.assertBetween(
            sample_decorr_time, correlation_time / 2, correlation_time * 2
        )

    final_sample = field_trajectory[-1]

    if run_correlation_length_check and variance is not None:
      with self.subTest('final_sample_correlation_len'):
        self.check_correlation_length(final_sample, correlation_length, grid)

    if run_mean_check:
      with self.subTest('final_sample_pointwise_mean'):
        self.check_mean(
            final_sample,
            grid,
            expected_mean=mean,
            variance=variance,
            correlation_length=correlation_length,
            mean_tol_in_standard_errs=mean_tol_in_standard_errs,
        )

    if run_variance_check:
      with self.subTest('final_sample_integrated_var'):
        self.check_variance(
            final_sample,
            ylm_transform,
            correlation_length=correlation_length,
            expected_variance=variance,
            var_tol_in_standard_errs=var_tol_in_standard_errs,
        )

  def check_independent(self, x, y):
    """Checks random field values x and y are independent."""
    self.assertEqual(x.ndim, 2)
    self.assertEqual(y.ndim, 2)
    corr = scipy.stats.pearsonr(x, y, axis=0).statistic
    standard_error = 2 / np.sqrt(x.shape[0])  # product of two iid χ²
    np.testing.assert_array_less(corr, 4 * standard_error)

  def check_nnx_state_structure_is_invariant(self, grf, grid):
    """Checks that random process does not mutate nnx.state(grf) structure."""
    init_nnx_state = nnx.state(grf, nnx.Param)
    random_state = grf.unconditional_sample(jax.random.key(0))
    random_state = grf.advance(random_state)
    _ = grf.state_values(grid, random_state)
    nnx_state = nnx.state(grf, nnx.Param)
    chex.assert_trees_all_equal_shapes_and_dtypes(init_nnx_state, nnx_state)


class GaussianRandomFieldTest(BaseSphericalHarmonicRandomProcessTest):
  """Tests GaussianRandomField random process."""

  @parameterized.named_parameters(
      dict(
          testcase_name='T42_reasonable_corrs',
          variance=0.7,
          ylm_transform=spherical_transforms.SphericalHarmonicsTransform(
              coordinates.LonLatGrid.T42(),
              coordinates.SphericalHarmonicGrid.T42(),
              partition_schema_key=None,
              mesh=parallelism.Mesh(),
          ),
          correlation_length=0.15,
          correlation_time=3,
      ),
      dict(
          testcase_name='T21_reasonable_corrs',
          variance=1.5,
          ylm_transform=spherical_transforms.SphericalHarmonicsTransform(
              coordinates.LonLatGrid.T21(),
              coordinates.SphericalHarmonicGrid.T21(),
              partition_schema_key=None,
              mesh=parallelism.Mesh(),
          ),
          correlation_length=0.15,
          correlation_time=3,
      ),
      dict(
          testcase_name='T42_large_radius',
          variance=1.2,
          ylm_transform=spherical_transforms.SphericalHarmonicsTransform(
              coordinates.LonLatGrid.T42(),
              coordinates.SphericalHarmonicGrid.T42(),
              partition_schema_key=None,
              radius=4.0,
              mesh=parallelism.Mesh(),
          ),
          correlation_length=1.15,
          correlation_time=3,
      ),
      dict(
          testcase_name='T85_long_corrs',
          variance=2.7,
          ylm_transform=spherical_transforms.SphericalHarmonicsTransform(
              coordinates.LonLatGrid.T85(),
              coordinates.SphericalHarmonicGrid.T85(),
              partition_schema_key=None,
              mesh=parallelism.Mesh(),
          ),
          correlation_length=0.5,
          correlation_time=3,
      ),
  )
  def test_unconditional_and_trajectory_stats(
      self,
      variance,
      ylm_transform,
      correlation_length,
      correlation_time,
  ):
    grf = random_processes.GaussianRandomField(
        ylm_transform=ylm_transform,
        dt=self.dt,
        sim_units=self.sim_units,
        correlation_time=correlation_time * typing.Quantity('1 hour'),
        correlation_length=correlation_length,
        variance=variance,
        rngs=nnx.Rngs(0),
    )
    self.check_unconditional_and_trajectory_stats(
        grf,
        0.0,  # mean = 0
        variance,
        ylm_transform,
        correlation_length,
        correlation_time,
    )

  @parameterized.named_parameters(
      dict(
          testcase_name='with_all_nnx_params',
          correlation_time_type=nnx.Param,
          correlation_length_type=nnx.Param,
          variance_type=nnx.Param,
      ),
      dict(
          testcase_name='with_fixed_params',
          correlation_time_type=random_processes.RandomnessParam,
          correlation_length_type=random_processes.RandomnessParam,
          variance_type=random_processes.RandomnessParam,
      ),
      dict(
          testcase_name='with_nnx_and_fixed_params',
          correlation_time_type=nnx.Param,
          correlation_length_type=nnx.Param,
          variance_type=random_processes.RandomnessParam,
      ),
  )
  def test_nnx_state_structure(
      self, correlation_time_type, correlation_length_type, variance_type
  ):
    """Tests that random process does not mutate structure of nnx.state."""
    ylm_transform = spherical_transforms.SphericalHarmonicsTransform(
        lon_lat_grid=coordinates.LonLatGrid.T42(),
        ylm_grid=coordinates.SphericalHarmonicGrid.T42(),
        partition_schema_key=None,
        mesh=parallelism.Mesh(),
    )
    grf = random_processes.GaussianRandomField(
        ylm_transform=ylm_transform,
        dt=self.dt,
        sim_units=self.sim_units,
        correlation_time=3 * typing.Quantity('1 hour'),
        correlation_length=0.15,
        variance=1.5,
        correlation_time_type=correlation_time_type,
        correlation_length_type=correlation_length_type,
        variance_type=variance_type,
        rngs=nnx.Rngs(0),
    )
    with self.subTest('nnx_state_structure_invariance'):
      self.check_nnx_state_structure_is_invariant(grf, ylm_transform.nodal_grid)

    with self.subTest('nnx_param_count'):
      params = nnx.state(grf, nnx.Param)
      actual_count = sum([np.size(x) for x in jax.tree.leaves(params)])
      expected_count = sum(
          x == nnx.Param
          for x in [
              correlation_time_type,
              correlation_length_type,
              variance_type,
          ]
      )
      self.assertEqual(actual_count, expected_count)


class BatchGaussianRandomFieldTest(BaseSphericalHarmonicRandomProcessTest):

  def setUp(self):
    super().setUp()
    self.ylm_transform = spherical_transforms.SphericalHarmonicsTransform(
        lon_lat_grid=coordinates.LonLatGrid.T85(),
        ylm_grid=coordinates.SphericalHarmonicGrid.T85(),
        partition_schema_key=None,
        mesh=parallelism.Mesh(),
    )

  def _make_grf(
      self,
      variances,
      correlation_lengths,
      correlation_times,
  ):
    return random_processes.BatchGaussianRandomField(
        ylm_transform=self.ylm_transform,
        dt=self.dt,
        sim_units=self.sim_units,
        correlation_times=correlation_times,
        correlation_lengths=correlation_lengths,
        variances=variances,
        rngs=nnx.Rngs(0),
    )

  @parameterized.named_parameters(
      dict(
          testcase_name='reasonable_corrs',
          variances=(1.0, 2.7),
          correlation_lengths=(0.15, 0.2),
          correlation_times=(1, 2.1),
      ),
  )
  def test_stats(
      self,
      variances,
      correlation_lengths,
      correlation_times,
  ):
    random_field = self._make_grf(
        variances, correlation_lengths, correlation_times
    )
    n_fields = len(variances)
    unroll_length = 10
    n_samples = 1000
    rngs = jax.random.split(jax.random.key(802701), n_samples)

    ###
    grid = self.ylm_transform.lon_lat_grid
    graph, params = nnx.split(random_field)
    sample_fn = lambda x: graph.apply(params).unconditional_sample(x)[0]
    evaluate_fn = lambda x: graph.apply(params).state_values(grid, x)[0]
    advance_fn = lambda x: graph.apply(params).advance(x)[0]
    batch_sample_fn = jax.vmap(sample_fn)
    batch_evaluate_fn = jax.vmap(evaluate_fn)
    batch_advance_fn = jax.vmap(advance_fn)
    initial_states = batch_sample_fn(rngs)
    initial_values = batch_evaluate_fn(initial_states).data

    def step_fn(c, _):
      next_c = batch_advance_fn(c)
      next_output = batch_evaluate_fn(next_c).data
      return (next_c, next_output)

    _, field_trajectory = jax.lax.scan(
        step_fn, initial_states, xs=None, length=unroll_length
    )
    field_trajectory = jax.device_get(field_trajectory)
    ###
    self.assertEqual(
        (unroll_length, n_samples, n_fields) + grid.shape,
        field_trajectory.shape,
    )
    final_nodal_value = field_trajectory[-1, ...]

    self.assertEqual(
        (n_samples, n_fields) + self.ylm_transform.modal_grid.shape,
        initial_states.core.shape,
    )

    # Nodal values should have the right statistics.
    for i, (variance, correlation_length) in enumerate(
        zip(variances, correlation_lengths, strict=True)
    ):
      for x in [initial_values, final_nodal_value]:
        self.check_mean(
            x[:, i],
            grid,
            expected_mean=0.0,
            variance=variance,
            correlation_length=correlation_length,
            mean_tol_in_standard_errs=5,
        )
        self.check_variance(
            x[:, i],
            self.ylm_transform,
            correlation_length=correlation_length,
            expected_variance=variance,
            var_tol_in_standard_errs=5,
        )
        self.check_correlation_length(
            x[:, i],
            expected_correlation_length=correlation_length,
            grid=grid,
        )

      # Fields 0 and 1 should be independent.
      # Check a handful of groups of nodal values.
      self.check_independent(
          x[:, 0, 100:105, 60],
          x[:, 1, 100:105, 60],
      )
      self.check_independent(
          x[:, 0, 100:105, 0],
          x[:, 1, 100:105, 0],
      )
      self.check_independent(x[:, 0, 0:5, 0], x[:, 1, 0:5, 0])

    # Initial and final sample should be independent as well, since we unroll
    # for much longer than the correlation time.
    self.check_independent(
        initial_values[:, 0, 50:55, 60],
        final_nodal_value[:, 0, 50:55, 60],
    )

  @parameterized.named_parameters(
      dict(
          testcase_name='with_all_nnx_params',
          correlation_time_type=nnx.Param,
          correlation_length_type=nnx.Param,
          variance_type=nnx.Param,
      ),
      dict(
          testcase_name='with_fixed_params',
          correlation_time_type=random_processes.RandomnessParam,
          correlation_length_type=random_processes.RandomnessParam,
          variance_type=random_processes.RandomnessParam,
      ),
      dict(
          testcase_name='with_nnx_and_fixed_params',
          correlation_time_type=nnx.Param,
          correlation_length_type=nnx.Param,
          variance_type=random_processes.RandomnessParam,
      ),
  )
  def test_nnx_state_structure(
      self, correlation_time_type, correlation_length_type, variance_type
  ):
    """Tests that random process does not mutate structure of nnx.state."""
    ylm_transform = spherical_transforms.SphericalHarmonicsTransform(
        lon_lat_grid=coordinates.LonLatGrid.T42(),
        ylm_grid=coordinates.SphericalHarmonicGrid.T42(),
        partition_schema_key=None,
        mesh=parallelism.Mesh(),
    )
    grid = ylm_transform.nodal_grid
    grf = random_processes.BatchGaussianRandomField(
        ylm_transform=ylm_transform,
        dt=self.dt,
        sim_units=self.sim_units,
        correlation_times=(1.0, 2.7),
        correlation_lengths=(0.15, 0.2),
        variances=(1, 2.1),
        correlation_time_type=correlation_time_type,
        correlation_length_type=correlation_length_type,
        variance_type=variance_type,
        rngs=nnx.Rngs(0),
    )
    with self.subTest('nnx_state_structure_invariance'):
      self.check_nnx_state_structure_is_invariant(grf, grid)

    with self.subTest('nnx_param_count'):
      params = nnx.state(grf, nnx.Param)
      actual_count = sum([np.size(x) for x in jax.tree.leaves(params)])
      expected_count = sum(
          grf.n_fields
          for x in [
              correlation_time_type,
              correlation_length_type,
              variance_type,
          ]
          if x == nnx.Param
      )
      self.assertEqual(actual_count, expected_count)

  def test_init_under_jit(self):
    """Tests that random process can be initialized under jit."""
    ylm_transform = spherical_transforms.SphericalHarmonicsTransform(
        lon_lat_grid=coordinates.LonLatGrid.T42(),
        ylm_grid=coordinates.SphericalHarmonicGrid.T42(),
        partition_schema_key=None,
        mesh=parallelism.Mesh(),
    )

    @nnx.jit
    def build_grf():
      grf = random_processes.BatchGaussianRandomField(
          ylm_transform=ylm_transform,
          dt=self.dt,
          sim_units=self.sim_units,
          correlation_times=(1.0, 2.7),
          correlation_lengths=(0.15, 0.2),
          variances=(1, 2.1),
          rngs=nnx.Rngs(0),
      )
      return grf

    grf = build_grf()
    self.assertEqual(grf.n_fields, 2)


class UncorrelatedRandomFieldsTest(parameterized.TestCase):
  """Tests Uncorrelated random processes."""

  @parameterized.named_parameters(
      dict(
          testcase_name='small_range',
          coord=coordinates.LonLatGrid.T42(),
          minval=-2,
          maxval=2,
      ),
      dict(
          testcase_name='large_range',
          coord=coordinates.LonLatGrid.T21(),
          minval=0,
          maxval=10_000,
      ),
  )
  def test_uniform_uncorrelated_stats(
      self,
      coord,
      minval,
      maxval,
  ):
    rng = nnx.Rngs(0)
    uniform = random_processes.UniformUncorrelated(coord, minval, maxval, rng)
    with self.subTest('unconditional_sample_stats'):
      sample = uniform.state_values().data
      mean_std_err = (maxval - minval) / np.sqrt(12 * math.prod(coord.shape))
      np.testing.assert_allclose(
          sample.mean(), (minval + maxval) / 2, atol=(3 * mean_std_err)
      )
      self.assertLess(sample.max(), maxval)
      self.assertGreaterEqual(sample.min(), minval)
    with self.subTest('advance_is_uncorrelated_from_initial_state'):
      sample = uniform.state_values().data
      uniform.advance()
      advanced_sample = uniform.state_values().data
      corr = scipy.stats.pearsonr(sample, advanced_sample, axis=None).statistic
      standard_error = 2 / np.sqrt(math.prod(sample.shape))
      np.testing.assert_array_less(corr, 4 * standard_error)

  @parameterized.named_parameters(
      dict(
          testcase_name='small_variance',
          coord=coordinates.LonLatGrid.T42(),
          mean=0.4,
          std=1.0,
      ),
      dict(
          testcase_name='large_variance',
          coord=coordinates.LonLatGrid.T21(),
          mean=20,
          std=5_000,
      ),
  )
  def test_normal_uncorrelated_stats(
      self,
      coord,
      mean,
      std,
  ):
    rng = nnx.Rngs(0)
    normal = random_processes.NormalUncorrelated(coord, mean, std, rng)
    with self.subTest('unconditional_sample_stats'):
      sample = normal.state_values().data
      mean_std_err = std / np.sqrt(math.prod(coord.shape))
      std_std_err = std / np.sqrt(2 * math.prod(coord.shape))
      np.testing.assert_allclose(sample.mean(), mean, atol=(3 * mean_std_err))
      np.testing.assert_allclose(sample.std(), std, atol=(3 * std_std_err))
    with self.subTest('advance_is_uncorrelated_from_initial_state'):
      sample = normal.state_values().data
      normal.advance()
      advanced_sample = normal.state_values().data
      corr = scipy.stats.pearsonr(sample, advanced_sample, axis=None).statistic
      standard_error = 2 / np.sqrt(math.prod(sample.shape))
      np.testing.assert_array_less(corr, 4 * standard_error)


if __name__ == '__main__':
  absltest.main()
