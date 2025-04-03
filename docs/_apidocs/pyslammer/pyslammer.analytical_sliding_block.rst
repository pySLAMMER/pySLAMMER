:py:mod:`pyslammer.analytical_sliding_block`
============================================

.. py:module:: pyslammer.analytical_sliding_block

.. autodoc2-docstring:: pyslammer.analytical_sliding_block
   :allowtitles:

Module Contents
---------------

Functions
~~~~~~~~~

.. list-table::
   :class: autosummary longtable
   :align: left

   * - :py:obj:`set_globals <pyslammer.analytical_sliding_block.set_globals>`
     - .. autodoc2-docstring:: pyslammer.analytical_sliding_block.set_globals
          :summary:
   * - :py:obj:`show_solution_approach <pyslammer.analytical_sliding_block.show_solution_approach>`
     - .. autodoc2-docstring:: pyslammer.analytical_sliding_block.show_solution_approach
          :summary:
   * - :py:obj:`create_harmonic_input_files <pyslammer.analytical_sliding_block.create_harmonic_input_files>`
     - .. autodoc2-docstring:: pyslammer.analytical_sliding_block.create_harmonic_input_files
          :summary:
   * - :py:obj:`find_harmonic_solution <pyslammer.analytical_sliding_block.find_harmonic_solution>`
     - .. autodoc2-docstring:: pyslammer.analytical_sliding_block.find_harmonic_solution
          :summary:
   * - :py:obj:`find_t1 <pyslammer.analytical_sliding_block.find_t1>`
     - .. autodoc2-docstring:: pyslammer.analytical_sliding_block.find_t1
          :summary:
   * - :py:obj:`find_t2 <pyslammer.analytical_sliding_block.find_t2>`
     - .. autodoc2-docstring:: pyslammer.analytical_sliding_block.find_t2
          :summary:
   * - :py:obj:`find_displacement <pyslammer.analytical_sliding_block.find_displacement>`
     - .. autodoc2-docstring:: pyslammer.analytical_sliding_block.find_displacement
          :summary:
   * - :py:obj:`apply_find_harmonic_solution <pyslammer.analytical_sliding_block.apply_find_harmonic_solution>`
     - .. autodoc2-docstring:: pyslammer.analytical_sliding_block.apply_find_harmonic_solution
          :summary:
   * - :py:obj:`harmonic_solutions <pyslammer.analytical_sliding_block.harmonic_solutions>`
     - .. autodoc2-docstring:: pyslammer.analytical_sliding_block.harmonic_solutions
          :summary:
   * - :py:obj:`harmonic_solution_plot <pyslammer.analytical_sliding_block.harmonic_solution_plot>`
     - .. autodoc2-docstring:: pyslammer.analytical_sliding_block.harmonic_solution_plot
          :summary:

Data
~~~~

.. list-table::
   :class: autosummary longtable
   :align: left

   * - :py:obj:`frequencies <pyslammer.analytical_sliding_block.frequencies>`
     - .. autodoc2-docstring:: pyslammer.analytical_sliding_block.frequencies
          :summary:
   * - :py:obj:`yield_accelerations <pyslammer.analytical_sliding_block.yield_accelerations>`
     - .. autodoc2-docstring:: pyslammer.analytical_sliding_block.yield_accelerations
          :summary:
   * - :py:obj:`combinations <pyslammer.analytical_sliding_block.combinations>`
     - .. autodoc2-docstring:: pyslammer.analytical_sliding_block.combinations
          :summary:
   * - :py:obj:`sample_resolution <pyslammer.analytical_sliding_block.sample_resolution>`
     - .. autodoc2-docstring:: pyslammer.analytical_sliding_block.sample_resolution
          :summary:

API
~~~

.. py:data:: frequencies
   :canonical: pyslammer.analytical_sliding_block.frequencies
   :value: 'array(...)'

   .. autodoc2-docstring:: pyslammer.analytical_sliding_block.frequencies

.. py:data:: yield_accelerations
   :canonical: pyslammer.analytical_sliding_block.yield_accelerations
   :value: 'array(...)'

   .. autodoc2-docstring:: pyslammer.analytical_sliding_block.yield_accelerations

.. py:data:: combinations
   :canonical: pyslammer.analytical_sliding_block.combinations
   :value: 'reshape(...)'

   .. autodoc2-docstring:: pyslammer.analytical_sliding_block.combinations

.. py:data:: sample_resolution
   :canonical: pyslammer.analytical_sliding_block.sample_resolution
   :value: 'array(...)'

   .. autodoc2-docstring:: pyslammer.analytical_sliding_block.sample_resolution

.. py:function:: set_globals()
   :canonical: pyslammer.analytical_sliding_block.set_globals

   .. autodoc2-docstring:: pyslammer.analytical_sliding_block.set_globals

.. py:function:: show_solution_approach()
   :canonical: pyslammer.analytical_sliding_block.show_solution_approach

   .. autodoc2-docstring:: pyslammer.analytical_sliding_block.show_solution_approach

.. py:function:: create_harmonic_input_files(freq, resolution, cycles=10)
   :canonical: pyslammer.analytical_sliding_block.create_harmonic_input_files

   .. autodoc2-docstring:: pyslammer.analytical_sliding_block.create_harmonic_input_files

.. py:function:: find_harmonic_solution(freq_val, ky_val, grav=9.81, plot=True)
   :canonical: pyslammer.analytical_sliding_block.find_harmonic_solution

   .. autodoc2-docstring:: pyslammer.analytical_sliding_block.find_harmonic_solution

.. py:function:: find_t1(a_in, ky, vals)
   :canonical: pyslammer.analytical_sliding_block.find_t1

   .. autodoc2-docstring:: pyslammer.analytical_sliding_block.find_t1

.. py:function:: find_t2(v_in, vb, vals, freq_val)
   :canonical: pyslammer.analytical_sliding_block.find_t2

   .. autodoc2-docstring:: pyslammer.analytical_sliding_block.find_t2

.. py:function:: find_displacement(v_in, vb, t1, t2, vals)
   :canonical: pyslammer.analytical_sliding_block.find_displacement

   .. autodoc2-docstring:: pyslammer.analytical_sliding_block.find_displacement

.. py:function:: apply_find_harmonic_solution(row, plot=False)
   :canonical: pyslammer.analytical_sliding_block.apply_find_harmonic_solution

   .. autodoc2-docstring:: pyslammer.analytical_sliding_block.apply_find_harmonic_solution

.. py:function:: harmonic_solutions(harmonic_combinations, save=False, plot=False)
   :canonical: pyslammer.analytical_sliding_block.harmonic_solutions

   .. autodoc2-docstring:: pyslammer.analytical_sliding_block.harmonic_solutions

.. py:function:: harmonic_solution_plot(a_in, v_in, vb, displacement, time, t1_def_val, t2_val, ky, vals, save=False)
   :canonical: pyslammer.analytical_sliding_block.harmonic_solution_plot

   .. autodoc2-docstring:: pyslammer.analytical_sliding_block.harmonic_solution_plot
