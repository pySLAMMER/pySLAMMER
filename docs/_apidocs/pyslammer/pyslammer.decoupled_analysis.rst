:py:mod:`pyslammer.decoupled_analysis`
======================================

.. py:module:: pyslammer.decoupled_analysis

.. autodoc2-docstring:: pyslammer.decoupled_analysis
   :allowtitles:

Module Contents
---------------

Classes
~~~~~~~

.. list-table::
   :class: autosummary longtable
   :align: left

   * - :py:obj:`Decoupled <pyslammer.decoupled_analysis.Decoupled>`
     - .. autodoc2-docstring:: pyslammer.decoupled_analysis.Decoupled
          :summary:

Functions
~~~~~~~~~

.. list-table::
   :class: autosummary longtable
   :align: left

   * - :py:obj:`mod_damp_testing <pyslammer.decoupled_analysis.mod_damp_testing>`
     - .. autodoc2-docstring:: pyslammer.decoupled_analysis.mod_damp_testing
          :summary:
   * - :py:obj:`strain_mod_update <pyslammer.decoupled_analysis.strain_mod_update>`
     - .. autodoc2-docstring:: pyslammer.decoupled_analysis.strain_mod_update
          :summary:
   * - :py:obj:`strain_damp_update <pyslammer.decoupled_analysis.strain_damp_update>`
     - .. autodoc2-docstring:: pyslammer.decoupled_analysis.strain_damp_update
          :summary:
   * - :py:obj:`impedance_damping <pyslammer.decoupled_analysis.impedance_damping>`
     - .. autodoc2-docstring:: pyslammer.decoupled_analysis.impedance_damping
          :summary:
   * - :py:obj:`constant_k_y <pyslammer.decoupled_analysis.constant_k_y>`
     - .. autodoc2-docstring:: pyslammer.decoupled_analysis.constant_k_y
          :summary:
   * - :py:obj:`interpolated_k_y <pyslammer.decoupled_analysis.interpolated_k_y>`
     - .. autodoc2-docstring:: pyslammer.decoupled_analysis.interpolated_k_y
          :summary:
   * - :py:obj:`assign_k_y <pyslammer.decoupled_analysis.assign_k_y>`
     - .. autodoc2-docstring:: pyslammer.decoupled_analysis.assign_k_y
          :summary:
   * - :py:obj:`some_ky_func <pyslammer.decoupled_analysis.some_ky_func>`
     - .. autodoc2-docstring:: pyslammer.decoupled_analysis.some_ky_func
          :summary:

Data
~~~~

.. list-table::
   :class: autosummary longtable
   :align: left

   * - :py:obj:`mrd_testing <pyslammer.decoupled_analysis.mrd_testing>`
     - .. autodoc2-docstring:: pyslammer.decoupled_analysis.mrd_testing
          :summary:
   * - :py:obj:`equivalent_linear_testing <pyslammer.decoupled_analysis.equivalent_linear_testing>`
     - .. autodoc2-docstring:: pyslammer.decoupled_analysis.equivalent_linear_testing
          :summary:
   * - :py:obj:`k_y_testing <pyslammer.decoupled_analysis.k_y_testing>`
     - .. autodoc2-docstring:: pyslammer.decoupled_analysis.k_y_testing
          :summary:

API
~~~

.. py:function:: mod_damp_testing(effective_strain, ref_strain)
   :canonical: pyslammer.decoupled_analysis.mod_damp_testing

   .. autodoc2-docstring:: pyslammer.decoupled_analysis.mod_damp_testing

.. py:function:: strain_mod_update(effective_strain, ref_strain)
   :canonical: pyslammer.decoupled_analysis.strain_mod_update

   .. autodoc2-docstring:: pyslammer.decoupled_analysis.strain_mod_update

.. py:function:: strain_damp_update(g_over_gmax, shear_strain, ref_strain)
   :canonical: pyslammer.decoupled_analysis.strain_damp_update

   .. autodoc2-docstring:: pyslammer.decoupled_analysis.strain_damp_update

.. py:function:: impedance_damping(vs_base, vs_slope)
   :canonical: pyslammer.decoupled_analysis.impedance_damping

   .. autodoc2-docstring:: pyslammer.decoupled_analysis.impedance_damping

.. py:function:: constant_k_y(k_y)
   :canonical: pyslammer.decoupled_analysis.constant_k_y

   .. autodoc2-docstring:: pyslammer.decoupled_analysis.constant_k_y

.. py:function:: interpolated_k_y(k_y)
   :canonical: pyslammer.decoupled_analysis.interpolated_k_y

   .. autodoc2-docstring:: pyslammer.decoupled_analysis.interpolated_k_y

.. py:function:: assign_k_y(k_y)
   :canonical: pyslammer.decoupled_analysis.assign_k_y

   .. autodoc2-docstring:: pyslammer.decoupled_analysis.assign_k_y

.. py:class:: Decoupled(ky: float or tuple[list[float], list[float]] or tuple[np.ndarray, np.ndarray] or callable, a_in: list[float] or np.ndarray, dt: float, height: int or float, vs_slope: int or float, vs_base: int or float, damp_ratio: float, ref_strain: float, scale_factor: float = 1, soil_model: str = 'linear_elastic', si_units: bool = True, lite: bool = False)
   :canonical: pyslammer.decoupled_analysis.Decoupled

   Bases: :py:obj:`pyslammer.sliding_block_analysis.SlidingBlockAnalysis`

   .. autodoc2-docstring:: pyslammer.decoupled_analysis.Decoupled

   .. rubric:: Initialization

   .. autodoc2-docstring:: pyslammer.decoupled_analysis.Decoupled.__init__

   .. py:method:: run_sliding_analysis()
      :canonical: pyslammer.decoupled_analysis.Decoupled.run_sliding_analysis

      .. autodoc2-docstring:: pyslammer.decoupled_analysis.Decoupled.run_sliding_analysis

   .. py:method:: sliding(i)
      :canonical: pyslammer.decoupled_analysis.Decoupled.sliding

      .. autodoc2-docstring:: pyslammer.decoupled_analysis.Decoupled.sliding

   .. py:method:: dynamic_response(i)
      :canonical: pyslammer.decoupled_analysis.Decoupled.dynamic_response

      .. autodoc2-docstring:: pyslammer.decoupled_analysis.Decoupled.dynamic_response

   .. py:method:: equivalent_linear()
      :canonical: pyslammer.decoupled_analysis.Decoupled.equivalent_linear

      .. autodoc2-docstring:: pyslammer.decoupled_analysis.Decoupled.equivalent_linear

.. py:data:: mrd_testing
   :canonical: pyslammer.decoupled_analysis.mrd_testing
   :value: False

   .. autodoc2-docstring:: pyslammer.decoupled_analysis.mrd_testing

.. py:data:: equivalent_linear_testing
   :canonical: pyslammer.decoupled_analysis.equivalent_linear_testing
   :value: False

   .. autodoc2-docstring:: pyslammer.decoupled_analysis.equivalent_linear_testing

.. py:data:: k_y_testing
   :canonical: pyslammer.decoupled_analysis.k_y_testing
   :value: False

   .. autodoc2-docstring:: pyslammer.decoupled_analysis.k_y_testing

.. py:function:: some_ky_func(disp)
   :canonical: pyslammer.decoupled_analysis.some_ky_func

   .. autodoc2-docstring:: pyslammer.decoupled_analysis.some_ky_func
