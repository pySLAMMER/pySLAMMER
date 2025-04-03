:py:mod:`pyslammer.rigid_analysis`
==================================

.. py:module:: pyslammer.rigid_analysis

.. autodoc2-docstring:: pyslammer.rigid_analysis
   :allowtitles:

Module Contents
---------------

Classes
~~~~~~~

.. list-table::
   :class: autosummary longtable
   :align: left

   * - :py:obj:`RigidAnalysis <pyslammer.rigid_analysis.RigidAnalysis>`
     - .. autodoc2-docstring:: pyslammer.rigid_analysis.RigidAnalysis
          :summary:

Data
~~~~

.. list-table::
   :class: autosummary longtable
   :align: left

   * - :py:obj:`M_TO_CM <pyslammer.rigid_analysis.M_TO_CM>`
     - .. autodoc2-docstring:: pyslammer.rigid_analysis.M_TO_CM
          :summary:
   * - :py:obj:`G_EARTH <pyslammer.rigid_analysis.G_EARTH>`
     - .. autodoc2-docstring:: pyslammer.rigid_analysis.G_EARTH
          :summary:

API
~~~

.. py:data:: M_TO_CM
   :canonical: pyslammer.rigid_analysis.M_TO_CM
   :value: 100

   .. autodoc2-docstring:: pyslammer.rigid_analysis.M_TO_CM

.. py:data:: G_EARTH
   :canonical: pyslammer.rigid_analysis.G_EARTH
   :value: 9.80665

   .. autodoc2-docstring:: pyslammer.rigid_analysis.G_EARTH

.. py:class:: RigidAnalysis(a_in, dt, ky, method='jibson')
   :canonical: pyslammer.rigid_analysis.RigidAnalysis

   Bases: :py:obj:`pyslammer.sliding_block_analysis.SlidingBlockAnalysis`

   .. autodoc2-docstring:: pyslammer.rigid_analysis.RigidAnalysis

   .. rubric:: Initialization

   .. autodoc2-docstring:: pyslammer.rigid_analysis.RigidAnalysis.__init__

   .. py:method:: __str__()
      :canonical: pyslammer.rigid_analysis.RigidAnalysis.__str__

   .. py:method:: jibson()
      :canonical: pyslammer.rigid_analysis.RigidAnalysis.jibson

      .. autodoc2-docstring:: pyslammer.rigid_analysis.RigidAnalysis.jibson

   .. py:method:: garcia_rivas_arnold()
      :canonical: pyslammer.rigid_analysis.RigidAnalysis.garcia_rivas_arnold

      .. autodoc2-docstring:: pyslammer.rigid_analysis.RigidAnalysis.garcia_rivas_arnold

   .. py:method:: downslope_dgr()
      :canonical: pyslammer.rigid_analysis.RigidAnalysis.downslope_dgr

      .. autodoc2-docstring:: pyslammer.rigid_analysis.RigidAnalysis.downslope_dgr

   .. py:method:: plot(acc: bool = True, vel: bool = True, disp: bool = True, gnd_motion: bool = False)
      :canonical: pyslammer.rigid_analysis.RigidAnalysis.plot

      .. autodoc2-docstring:: pyslammer.rigid_analysis.RigidAnalysis.plot
