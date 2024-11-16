:py:mod:`pyslammer.record`
==========================

.. py:module:: pyslammer.record

.. autodoc2-docstring:: pyslammer.record
   :allowtitles:

Module Contents
---------------

Classes
~~~~~~~

.. list-table::
   :class: autosummary longtable
   :align: left

   * - :py:obj:`GroundMotion <pyslammer.record.GroundMotion>`
     - .. autodoc2-docstring:: pyslammer.record.GroundMotion
          :summary:

API
~~~

.. py:class:: GroundMotion(accel: np.ndarray or list, dt: float, name: str = 'None')
   :canonical: pyslammer.record.GroundMotion

   .. autodoc2-docstring:: pyslammer.record.GroundMotion

   .. rubric:: Initialization

   .. autodoc2-docstring:: pyslammer.record.GroundMotion.__init__

   .. py:method:: __str__()
      :canonical: pyslammer.record.GroundMotion.__str__

   .. py:method:: _calc_gnd_params()
      :canonical: pyslammer.record.GroundMotion._calc_gnd_params

      .. autodoc2-docstring:: pyslammer.record.GroundMotion._calc_gnd_params

   .. py:method:: scale(pga: float = False, scale_factor: float = False)
      :canonical: pyslammer.record.GroundMotion.scale

      .. autodoc2-docstring:: pyslammer.record.GroundMotion.scale

   .. py:method:: unscale()
      :canonical: pyslammer.record.GroundMotion.unscale

      .. autodoc2-docstring:: pyslammer.record.GroundMotion.unscale

   .. py:method:: invert()
      :canonical: pyslammer.record.GroundMotion.invert

      .. autodoc2-docstring:: pyslammer.record.GroundMotion.invert

   .. py:method:: uninvert()
      :canonical: pyslammer.record.GroundMotion.uninvert

      .. autodoc2-docstring:: pyslammer.record.GroundMotion.uninvert

   .. py:method:: plot(acc: bool = True, vel: bool = True, disp: bool = True, enable: bool = True, called: bool = False)
      :canonical: pyslammer.record.GroundMotion.plot

      .. autodoc2-docstring:: pyslammer.record.GroundMotion.plot
