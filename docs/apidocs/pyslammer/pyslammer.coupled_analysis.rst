:py:mod:`pyslammer.coupled_analysis`
====================================

.. py:module:: pyslammer.coupled_analysis

.. autodoc2-docstring:: pyslammer.coupled_analysis
   :allowtitles:

Module Contents
---------------

Classes
~~~~~~~

.. list-table::
   :class: autosummary longtable
   :align: left

   * - :py:obj:`Coupled <pyslammer.coupled_analysis.Coupled>`
     - .. autodoc2-docstring:: pyslammer.coupled_analysis.Coupled
          :summary:

Functions
~~~~~~~~~

.. list-table::
   :class: autosummary longtable
   :align: left

   * - :py:obj:`some_ky_func <pyslammer.coupled_analysis.some_ky_func>`
     - .. autodoc2-docstring:: pyslammer.coupled_analysis.some_ky_func
          :summary:

Data
~~~~

.. list-table::
   :class: autosummary longtable
   :align: left

   * - :py:obj:`equivalent_linear_testing <pyslammer.coupled_analysis.equivalent_linear_testing>`
     - .. autodoc2-docstring:: pyslammer.coupled_analysis.equivalent_linear_testing
          :summary:
   * - :py:obj:`k_y_testing <pyslammer.coupled_analysis.k_y_testing>`
     - .. autodoc2-docstring:: pyslammer.coupled_analysis.k_y_testing
          :summary:

API
~~~

.. py:class:: Coupled(ky: float or tuple[list[float], list[float]] or tuple[np.ndarray, np.ndarray] or callable, a_in: list[float] or np.ndarray, dt: float, height: int or float, vs_slope: int or float, vs_base: int or float, damp_ratio: float, ref_strain: float, scale_factor: float = 1, soil_model: str = 'linear_elastic', si_units: bool = True, lite: bool = False)
   :canonical: pyslammer.coupled_analysis.Coupled

   Bases: :py:obj:`pyslammer.decoupled_analysis.Decoupled`

   .. autodoc2-docstring:: pyslammer.coupled_analysis.Coupled

   .. rubric:: Initialization

   .. autodoc2-docstring:: pyslammer.coupled_analysis.Coupled.__init__

   .. py:method:: run_sliding_analysis()
      :canonical: pyslammer.coupled_analysis.Coupled.run_sliding_analysis

      .. autodoc2-docstring:: pyslammer.coupled_analysis.Coupled.run_sliding_analysis

   .. py:method:: coupled_sliding(i)
      :canonical: pyslammer.coupled_analysis.Coupled.coupled_sliding

      .. autodoc2-docstring:: pyslammer.coupled_analysis.Coupled.coupled_sliding

   .. py:method:: coupled_setupstate(i)
      :canonical: pyslammer.coupled_analysis.Coupled.coupled_setupstate

      .. autodoc2-docstring:: pyslammer.coupled_analysis.Coupled.coupled_setupstate

   .. py:method:: solvu(i)
      :canonical: pyslammer.coupled_analysis.Coupled.solvu

      .. autodoc2-docstring:: pyslammer.coupled_analysis.Coupled.solvu

   .. py:method:: c_slideacc(i)
      :canonical: pyslammer.coupled_analysis.Coupled.c_slideacc

      .. autodoc2-docstring:: pyslammer.coupled_analysis.Coupled.c_slideacc

   .. py:method:: c_slidingcheck(i)
      :canonical: pyslammer.coupled_analysis.Coupled.c_slidingcheck

      .. autodoc2-docstring:: pyslammer.coupled_analysis.Coupled.c_slidingcheck

   .. py:method:: slidestop(i)
      :canonical: pyslammer.coupled_analysis.Coupled.slidestop

      .. autodoc2-docstring:: pyslammer.coupled_analysis.Coupled.slidestop

.. py:data:: equivalent_linear_testing
   :canonical: pyslammer.coupled_analysis.equivalent_linear_testing
   :value: False

   .. autodoc2-docstring:: pyslammer.coupled_analysis.equivalent_linear_testing

.. py:data:: k_y_testing
   :canonical: pyslammer.coupled_analysis.k_y_testing
   :value: False

   .. autodoc2-docstring:: pyslammer.coupled_analysis.k_y_testing

.. py:function:: some_ky_func(disp)
   :canonical: pyslammer.coupled_analysis.some_ky_func

   .. autodoc2-docstring:: pyslammer.coupled_analysis.some_ky_func
