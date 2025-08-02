"""Define object to keep a single instrument measurements."""

import inspect
import logging
from abc import ABC
from typing import Callable, Self

import numpy as np
import pandas as pd
from matplotlib.axes import Axes
from matplotlib.container import StemContainer
from matplotlib.lines import Line2D
from multipac_testbench.util.filtering import (
    array_is_growing,
    remove_isolated_false,
    remove_trailing_true,
)
from multipac_testbench.util.types import CALLBACK_T, POST_TREATER_T
from numpy.typing import NDArray


class Instrument(ABC):
    """Hold measurements of a single instrument."""

    _raw_data_can_change = False

    def __init__(
        self,
        name: str,
        data: pd.Series | None,
        position: NDArray[np.float64] | float,
        is_2d: bool = False,
        color: tuple[float, float, float] | None = None,
        is_raw: bool = False,
        **kwargs,
    ) -> None:
        """Instantiate the class.

        Parameters
        ----------
        name :
            Name of the instrument.
        data :
            ``x`` and ``y`` data as saved in the ``CSV`` produced by LabVIEW.
            Can be ``None`` in specific cases, e.g. :class:`.Reconstructed`.
        position :
            The position of the instrument. If irrelevant (global diagnostic),
            must be set to ``np.nan``.
        is_2d :
            To make the difference between instruments holding a single array
            of data (e.g. current vs time) and those holding several columns
            (eg forward and reflected power).
        color :
            Color for the plots; all instruments from a same :class:`.PickUp`
            have the same. The default is None, which happens for instruments
            defined in a :class:`.GlobalDiagnostics`.
        is_raw :
            If set to ``True``, the functions defined in
            :attr:`._transfer_functions` are directly appended to the list of
            post-treaters. They are used to convert raw data (ie: acquisition
            voltages) to physical quantities.
        kwargs :
            Additional keyword arguments coming from the ``TOML`` configuration
            file.

        """
        self.name = name
        logging.debug(
            f"Creating a {self.__class__.__name__} named {name} at "
            f"{position = }. It has {len(data) if data is not None else 0}"
            " points."
        )

        #: The position of the instrument. If irrelevant (global diagnostic),
        #: must be set to ``np.nan``.
        self.position = position

        self.is_2d = is_2d
        self.color = color
        plotters = self._get_plot_methods(is_2d)
        self.plot_vs_position, self.scatter_data = plotters

        self.__raw_data: pd.Series
        if data is not None:
            self.__raw_data = data
        self._data: NDArray[np.float64]
        self._data_as_pd: pd.Series | pd.DataFrame

        self._post_treaters: list[POST_TREATER_T] = []
        self._is_raw = is_raw
        if is_raw:
            for func in self._transfer_functions:
                self.add_post_treater(func)

        #: Functions to call when a post-treater is added to current object.
        #:
        #: .. seealso::
        #:    :meth:`register_callback`
        #:
        self._callbacks: list[CALLBACK_T] = []

    def __str__(self) -> str:
        """Give concise information on instrument."""
        out = f"{self.class_name} ({self.name})"
        return out

    @classmethod
    def ylabel(cls) -> str:
        """Label used for plots."""
        return "default ylabel"

    @property
    def label(self) -> str | None:
        """Label used for legends in plots vs position."""
        return

    @classmethod
    def from_pd_dataframe(
        cls,
        name: str,
        raw_data: pd.DataFrame,
        **kwargs,
    ) -> Self:
        """Instantiate the object from several ``CSV`` file columns.

        Parameters
        ----------
        name :
            Name of the instrument.
        raw_data :
            Object holding several columns of the ``CSV``.
        kwargs :
            Other keyword arguments passed to the :class:`.Instrument`.

        Returns
        -------
            An instrument. Note that its ``data`` attribute will be a 2D
            array.

        """
        is_2d = True
        return cls(name, raw_data, is_2d=is_2d, **kwargs)

    @property
    def class_name(self) -> str:
        """Get the name of the instrument class."""
        return self.__class__.__name__

    @property
    def _transfer_functions(self) -> list[POST_TREATER_T]:
        """
        Give functions transforming acquisition voltage to physical quantity.

        They are used when input files contain raw data, ie acquisition
        voltages.

        """
        logging.warning(
            f"{self} has no transfer function defined, so its ``data``"
            " attribute will hold acquisition voltage in volt rather than any "
            "meaningful physical quantity."
        )
        return []

    @property
    def _raw_data(self) -> pd.Series:
        """Raw data as measured by the instrument.

        For classic :class:`.Instrument`, it should not change. For
        :class:`.VirtualInstrument`, it may change when the data it is
        calculated changes.

        """
        return self.__raw_data

    @_raw_data.setter
    def _raw_data(self, new_value: pd.Series) -> None:
        """Updates the :property:`_raw_data` value.

        This method will raise an error for classic :class:`.Instrument`, as
        `raw_data` is a column in the data file. It may however be changed for
        :class:`.VirtualInstrument`.

        """
        if not self._raw_data_can_change:
            raise ValueError(
                "._raw_data should not be updated. If you need to do so "
                "anyway, set ._raw_data_can_change to True."
            )
        self.__raw_data = new_value
        for dependent in ("_data", "_data_as_pd"):
            if hasattr(self, dependent):
                delattr(self, dependent)

    @property
    def data(self) -> NDArray[np.float64]:
        """Get the treated data.

        Note that in order to save time, ``_data`` is not re-calculated
        from ``raw_data`` every time. Hence, it is primordial to re-set
        ``_y_data`` to ``None`` every time a change is made to
        ``_post_treaters``.

        """
        if not hasattr(self, "_data"):
            self._data = self._post_treat(self._raw_data.to_numpy())
        return self._data

    @data.setter
    def data(self, new_data: NDArray[np.float64]) -> None:
        """Set ``data``, clean previous ``_data_as_pd``."""
        self._data = new_data
        if hasattr(self, "_data_as_pd"):
            delattr(self, "_data_as_pd")

    @property
    def data_as_pd(self) -> pd.Series | pd.DataFrame:
        """Get the treated data as a pandas object."""
        if hasattr(self, "_data_as_pd"):
            return self._data_as_pd

        index = self._raw_data.index
        if self.is_2d:
            assert isinstance(self._raw_data, pd.DataFrame)
            columns = self._raw_data.columns
            self._data_as_pd = pd.DataFrame(
                self.data, columns=columns, index=index
            )
            return self._data_as_pd

        self._data_as_pd = pd.Series(self.data, index=index, name=self.name)
        return self._data_as_pd

    def register_callback(self, cb: CALLBACK_T) -> None:
        """Register the callback function.

        Callback functions are called when a post-treater is added to ``Self``.
        This is used when :class:`.VirtualInstrument` data depends on some
        other :class:`.Instrument` data.
        Currently used for:

        - :class:`.ForwardPower` (updates :class:`.ReflectionCoefficient`)
        - :class:`.ReflectedPower` (updates :class:`.ReflectionCoefficient`)
        - :class:`.ReflectionCoefficient` (updates :class:`.SWR`)

        """
        self._callbacks.append(cb)
        logging.debug(f"Registered callback {cb} in {self}.")

    def _notify_callbacks(self) -> None:
        """Call all callback functions."""
        if len(getattr(self, "_callbacks", [])) == 0:
            return

        for cb in self._callbacks:
            if inspect.ismethod(cb):
                owner = cb.__self__.__class__.__name__
            else:
                owner = repr(cb)

            logging.info(
                f"Using new data from {self} to recompute data in {owner}."
            )
            cb()

    @property
    def post_treaters(self) -> list[POST_TREATER_T]:
        """Get the list of the post-treating functions."""
        return self._post_treaters

    @post_treaters.setter
    def post_treaters(self, post_treaters: list[POST_TREATER_T]) -> None:
        """Set the full list of post-treating functions at once.

        Parameters
        ----------
        post_treaters :
            Post-treating functions.

        """
        delattr(self, "_data")
        delattr(self, "_data_as_pd")
        self._post_treaters = post_treaters

    def add_post_treater(self, post_treater: POST_TREATER_T) -> None:
        """Append a single post-treating function.

        Parameters
        ----------
        post_treater :
            Post-treating function to add. It must take an array as input, and
            return an array with the same size as output.

        """
        logging.debug(f"Adding a post_treater to {self}.")
        if hasattr(self, "_data"):
            delattr(self, "_data")
        if hasattr(self, "_data_as_pd"):
            delattr(self, "_data_as_pd")
        self._post_treaters.append(post_treater)
        self._notify_callbacks()

    def _post_treat(self, data: NDArray[np.float64]) -> NDArray[np.float64]:
        """Apply all post-treatment functions."""
        original_data_shape = data.shape
        for post_treater in self.post_treaters:
            data = post_treater(data)
            if original_data_shape != data.shape:
                logging.error(
                    f"The post treater {post_treater} modified the shape of "
                    "the array."
                )
        return data

    def _get_plot_methods(self, is_2d: bool) -> tuple[Callable, Callable]:
        """Give the proper plotting functions according to ``is_2d``."""
        plotters = (self._plot_vs_position_for_1d, self._scatter_data_1d)
        if is_2d:
            plotters = (self._plot_vs_position_for_2d, self._scatter_data_2d)
        return plotters

    def _plot_vs_position_for_1d(
        self,
        sample_index: int,
        raw: bool = False,
        color: tuple[float, float, float] | None = None,
        artist: StemContainer | None = None,
        axe: Axes | None = None,
        **kwargs,
    ) -> StemContainer:
        """Plot what instrument measured at its position, at a given time step.

        Adapted to Pick-Up instruments.

        Parameters
        ----------
        sample_index :
            Index of the measurements.
        raw :
            If the raw data should be plotted.
        color :
            Color of the plot.
        artist :
            If provided, the stem Artist object is updated rather than
            overwritten. It is mandatory for matplotlib animation to work.
        axe :
            Axe where the artist should be created. It must be provided if
            ``artist`` is not given.

        Returns
        -------
            The plotted stem.

        """
        position = getattr(self, "position", -1.0)
        assert isinstance(position, float)

        data = self.data[sample_index]
        if raw or len(self.post_treaters) == 0:
            data = self._raw_data[sample_index]

        if artist is not None:
            artist[0].set_ydata([data])
            new_path = np.array([[position, 0.0], [position, data]])
            artist[1].set_paths([new_path])
            return artist

        assert axe is not None
        artist = axe.stem(position, data, label=self.label, **kwargs)
        return artist

    def _plot_vs_position_for_2d(
        self,
        sample_index: int,
        raw: bool = False,
        color: tuple[float, float, float] | None = None,
        axe: Axes | None = None,
        artist: Line2D | None = None,
        **kwargs,
    ) -> Line2D:
        """
        Plot what instrument measured at all positions, at a given time step.

        Adapted to instruments with several positions, such as
        VirtualInstrument reproducing electric field envelope at all positions.

        Parameters
        ----------
        sample_index :
            Index of the measurements.
        raw :
            If the raw data should be plotted.
        color :
            Color of the plot.
        artist :
            If provided, the Line2D Artist object is updated rather than
            overwritten. It is mandatory for matplotlib animation to work.
        axe :
            Axe where the artist should be created. It must be provided if
            ``artist`` is not given.

        Returns
        -------
            The plotted line.

        """
        assert hasattr(self, "position")
        assert isinstance(self.position, np.ndarray)

        data = self.data[sample_index, :]
        assert isinstance(data, np.ndarray)
        assert data.shape == self.position.shape

        if artist is not None:
            artist.set_data(self.position, data)
            return artist

        assert axe is not None
        (artist,) = axe.plot(
            self.position, data, color=color, label=self.label, **kwargs
        )
        axe.legend()
        return artist

    def _scatter_data_1d(
        self,
        axes: Axes,
        multipactor: NDArray[np.bool],
        xdata: float | NDArray[np.float64] | None = None,
    ) -> None:
        """Plot ``data``, discriminating where there is multipactor or not.

        Parameters
        ----------
        axes :
            Where to plot.
        multipactor :
            True where there is multipactor, False elsewhere.
        xdata :
            x position of the data. The default is None, in which case we take
            :attr:`position`.

        """
        data = self.data

        if xdata is None:
            xdata = self.position
        if isinstance(xdata, float):
            xdata = np.full(len(data), xdata)
        assert isinstance(xdata, np.ndarray)

        mp_kwargs = {
            "c": "r",
            "marker": "s",
            "alpha": 0.1,
        }
        no_mp_kwargs = {
            "c": "k",
            "alpha": 0.1,
            "marker": "x",
        }
        if axes.get_legend_handles_labels() == ([], []):
            mp_kwargs["label"] = "MP"
            no_mp_kwargs["label"] = "No MP"

        axes.scatter(xdata[multipactor] - 0.1, data[multipactor], **mp_kwargs)
        axes.scatter(
            xdata[~multipactor] + 0.1, data[~multipactor], **no_mp_kwargs
        )
        return

    def _scatter_data_2d(self, *args, **kwargs) -> None:
        """Hold place."""
        raise NotImplementedError()

    def growth_mask(
        self,
        minimum_number_of_points: int = 0,
        n_trailing_points_to_check: int = 0,
        width: int = 10,
        **kwargs,
    ) -> NDArray[np.bool]:
        """Identify regions where the signal is increasing ("growing").

        This method analyzes a signal to determine where it exhibits a growing
        trend. It returns a boolean array of the same length as the input
        signal, where ``True`` indicates a region of growth and ``False``
        otherwise.
        *A priori*, will be useful for:

        - :class:`.PowerSetpoint` to determine power cycles. A fallback is
          :class:`.ForwardPower`.
        - :class:`.RPA`.

        The method performs three main operations:

        #. It uses a sliding-window heuristic (*via* :func:`.array_is_growing`)
           to detect growth.
        #. It removes short, isolated ``False`` segments, enforcing a minimum
           number of consecutive ``True`` values to be considered valid.
        #. It clears any trailing ``True`` values near the end of the array to
           prevent spurious detections due to edge effects.

        Parameters
        ----------
        minimum_number_of_points :
            The minimum number of consecutive ``True`` values required to
            consider a region as growing. Shorter segments are suppressed.
        n_trailing_points_to_check :
            The number of points at the end of the signal to check and force to
            ``False`` if they form an isolated or uncertain growth pattern.
            Particulatly useful for :class:`.ForwardPower` to avoid detection
            of a new power cycle at the end of the test.
        width :
            Width of the sample to determine increase.
        **kwargs :
            Additional keyword arguments passed to :func:`.array_is_growing`.

        Returns
        -------
            Boolean array indicating where the signal is growing.

        Notes
        -----
        - The detection is influenced by the choice of parameters and the
          behavior of :func:`.array_is_growing`.
        - Trailing regions and short noise-like fluctuations are filtered out.

        .. todo::
           Consider adding post-processing to remove isolated ``True`` values.

        """
        n_points = len(self._raw_data)
        is_growing: list[bool] = []

        local_is_growing = True
        for i in range(n_points):
            local_is_growing = array_is_growing(
                self.data,
                i,
                no_change_value=local_is_growing,
                width=width,
                **kwargs,
            )

            is_growing.append(local_is_growing)

        growth_mask = np.array(is_growing, dtype=np.bool)

        # Remove isolated False (useful for noisy instruments)
        if minimum_number_of_points > 0:
            growth_mask = remove_isolated_false(
                growth_mask, minimum_number_of_points
            )

        # Ensure that last growth is False (useful for Power)
        if n_trailing_points_to_check > 0:
            growth_mask = remove_trailing_true(
                growth_mask,
                n_trailing_points_to_check,
                array_name_for_warning=str(self.__class__.__name__),
            )

        return growth_mask

    def growth_array(
        self,
        **kwargs,
    ) -> NDArray[np.float64]:
        """Identify regions where the signal is increasing ("growing").

        This method analyzes a signal to determine where it exhibits a growing
        trend. It returns a float array of the same length as the input
        signal, where ``1.0`` indicates a region of growth and ``-1.0``
        otherwise. ``0.0`` means constant signal.
        *A priori*, will be useful for:

        - :class:`.PowerSetpoint` to determine power cycles

        Notes
        -----
        Designed for non-noisy instruments such as :class:`.PowerSetpoint`.

        Parameters
        ----------
        width :
            Width of the sample to determine increase.
        no_change_value :
            Value to put in growth mask when we did not manage to find whether
            measured signal increased or not.
        **kwargs :
            Additional keyword arguments passed to :func:`.array_is_growing`.

        Returns
        -------
            Array where +1 means growing, -1 decreasing, 0 means constant.

        """
        bool_to_float = {True: 1.0, False: -1.0, None: 0.0}
        is_growing = [
            bool_to_float[
                array_is_growing(
                    self.data,
                    i,
                    width=2,
                    no_change_value=None,
                    default_first_value=None,
                    **kwargs,
                )
            ]
            for i in range(len(self._raw_data))
        ]
        is_growing[-1] = 0.0
        return np.array(is_growing, dtype=np.float64)
