# (C) Copyright 2024- ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
#
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.

import io
import warnings
import io
from collections import defaultdict
from typing import Optional

import earthkit.data as ekd
from earthkit.workflows import mark
from earthkit.workflows.decorators import as_payload
from earthkit.workflows.plugins.anemoi.fluent import ENSEMBLE_DIMENSION_NAME
from forecastbox.models import Model
from forecastbox.products.ensemble import BaseEnsembleProduct
from forecastbox.products.product import GenericTemporalProduct

from ..rjsf import FieldWithUI
from ..rjsf import StringSchema
from ..rjsf import UIStringField
from . import plot_product_registry
from ..rjsf import FieldWithUI, StringSchema, IntegerSchema, ArraySchema, UIObjectField, UIStringField, FieldSchema

EARTHKIT_PLOTS_IMPORTED = True
try:
    from earthkit.plots import Figure
    from earthkit.plots import Subplot
except ImportError:
    from typing import Any

    EARTHKIT_PLOTS_IMPORTED = False
    Figure = Any
    Subplot = Any

WIND_SHORTNAMES = ["u", "v", "10u", "10v", "100u", "100v"]


def _plot_fields(subplot: Subplot, fields: ekd.FieldList, **kwargs: dict[str, dict]) -> None:
    """Plot fields on a subplot, using the appropriate plotting method based on field metadata.

    Will attempt to group related plots, and call the appropriate plotting method.

    Parameters
    ----------
    subplot : Subplot
        Subplot to plot on.
    fields : ekd.FieldList
        FieldList to iterate over and plot.
    kwargs : dict[str, dict]
        Additional keyword arguments for each plotting methods,
        Top level keys are the method names, and values are dictionaries of keyword arguments for that method.
    """
    plot_categories = defaultdict(lambda: defaultdict(list))
    for index, field in enumerate(fields):
        if field.metadata().get("shortName", None) in WIND_SHORTNAMES:
            plot_categories["quiver"][field.metadata().get("levtype", None)].append(field)
            continue
        plot_categories["quickplot"][index].append(field)

    for method, comp in plot_categories.items():
        for sub_cat, sub_fields in comp.items():
            try:
                getattr(subplot, method)(ekd.FieldList.from_fields(sub_fields), **kwargs.get(method, {}))
            except Exception as err:
                if method == "quickplot":
                    raise err
                subplot.quickplot(
                    ekd.FieldList.from_fields(sub_fields),
                    **kwargs.get("quickplot", {}),
                )

@as_payload
@mark.environment_requirements(["earthkit-plots"])
def export(figure: Figure, format: str = "png") -> tuple[bytes, str]:
    """
    Export a figure to a specified format.

    Parameters
    ----------
    figure : Figure
        The figure to export.
    format : str
        The format to export the figure to. Supported formats are 'png', 'pdf', 'svg'.

    Returns
    -------
    tuple[bytes, str]
        A tuple containing the serialized data as bytes and the MIME type.
    """
    if format not in ["png", "pdf", "svg"]:
        raise ValueError(f"Unsupported format: {format}. Supported formats are 'png', 'pdf', 'svg'.")
    
    buf = io.BytesIO()
    figure.save(buf, format=format)

    return buf.getvalue(), f"image/{format}"

@as_payload
@mark.environment_requirements(["earthkit-plots"])
def export(figure: Figure, format: str = "png") -> tuple[bytes, str]:
    """Export a figure to a specified format.

    Parameters
    ----------
    figure : Figure
        The figure to export.
    format : str
        The format to export the figure to. Supported formats are 'png', 'pdf', 'svg'.

    Returns
    -------
    tuple[bytes, str]
        A tuple containing the serialized data as bytes and the MIME type.
    """
    if format not in ["png", "pdf", "svg"]:
        raise ValueError(f"Unsupported format: {format}. Supported formats are 'png', 'pdf', 'svg'.")

    buf = io.BytesIO()
    figure.save(buf, format=format)

    return buf.getvalue(), f"image/{format}"


@as_payload
@mark.environment_requirements(["earthkit-plots", "earthkit-plots-default-styles"])
def quickplot(
    fields: ekd.FieldList,
    groupby: Optional[str] = None,
    subplot_title: Optional[str] = None,
    figure_title: Optional[str] = None,
    domain: Optional[str] = None,
):
    from earthkit.plots import Figure  # NOTE we need to import again to mask the possible Any
    from earthkit.plots.components import layouts
    from earthkit.plots.schemas import schema
    from earthkit.plots.utils import iter_utils

    if not isinstance(fields, ekd.FieldList):
        fields = ekd.FieldList.from_fields(fields)

    if groupby:
        unique_values = iter_utils.flatten(arg.metadata(groupby) for arg in fields)
        unique_values = list(dict.fromkeys(unique_values))

        grouped_data = {val: fields.sel(**{groupby: val}) for val in unique_values}
    else:
        grouped_data = {None: fields}

    n_plots = len(grouped_data)

    rows, columns = layouts.rows_cols(n_plots)

    figure = Figure(rows=rows, columns=columns)

    if subplot_title is None and groupby is not None:
        subplot_title = f"{{{groupby}}}"

    for i, (group_val, group_args) in enumerate(grouped_data.items()):
        subplot = figure.add_map(domain=domain)
        _plot_fields(subplot, group_args, quickplot=dict(interpolate=True))

        for m in schema.quickmap_subplot_workflow:
            args = []
            if m == "title":
                args = [subplot_title]
            try:
                getattr(subplot, m)(*args)
            except Exception as err:
                warnings.warn(
                    f"Failed to execute {m} on given data with: \n"
                    f"{err}\n\n"
                    "consider constructing the plot manually."
                )

    for m in schema.quickmap_figure_workflow:
        try:
            getattr(figure, m)()
        except Exception as err:
            warnings.warn(
                f"Failed to execute {m} on given data with: \n" f"{err}\n\n" "consider constructing the plot manually."
            )

    # figure.title(figure_title)

    return figure


class MapProduct(GenericTemporalProduct):
    """Map Product.

    This product is a simple wrapper around the `earthkit.plots` library to create maps.

    # TODO, Add projection, and title control
    """

    domains = ["Global", "Europe", "Australia", "Malawi", "Norway"]

    @property
    def formfields(self):
        formfields = super().formfields.copy()
        formfields.update(
            reduce=FieldWithUI(
                jsonschema=StringSchema(
                    title="Reduce",
                    description="Combine all steps and parameters into a single plot",
                    enum=["True", "False"],
                    default="True",
                )
            ),
            domain=FieldWithUI(
                jsonschema=StringSchema(
                    title="Domain",
                    description="Domain of the map",
                    enum=self.domains,
                    default="Global",
                ),
                ui=UIStringField(
                    widget="select",
                ),
            ),
        )
        return formfields

    @property
    def model_assumptions(self):
        return {
            "domain": self.domains,
            "reduce": ["True", "False"],
        }

    @property
    def qube(self):
        return self.make_generic_qube(domain=self.domains, reduce=["True", "False"])

    def validate_intersection(self, model: Model) -> bool:
        return super().validate_intersection(model) and EARTHKIT_PLOTS_IMPORTED


@plot_product_registry("Maps")
class SimpleMapProduct(MapProduct):

    def execute(self, product_spec, model, source):
        domain = product_spec.pop("domain", None)
        source = self.select_on_specification(product_spec, source)

        if domain == "Global":
            domain = None

        if product_spec.get("reduce", "True") == "True":
            source = source.concatenate("param")
            source = source.concatenate("step")

        quickplot_payload = quickplot(
            domain=domain,
            groupby="valid_datetime",
            subplot_title="T+{lead_time}",
            figure_title="{variable_name} over {domain}\n Base time: {base_time: %Y%m%dT%H%M}\n",
        )
        plots = source.map(quickplot_payload).map(export(format="png")).map(self.named_payload("Map"))

        return plots


@plot_product_registry("Ensemble Maps")
class EnsembleMapProduct(BaseEnsembleProduct, MapProduct):
    """Ensemble Map Product.

    Create a subplotted map with each subplot being a different ensemble member.
    """

    def execute(self, product_spec, model, source):
        domain = product_spec.pop("domain", None)
        source = self.select_on_specification(product_spec, source)

        if domain == "Global":
            domain = None

        source = source.concatenate(ENSEMBLE_DIMENSION_NAME)
        source = source.concatenate("param")

        quickplot_payload = quickplot(
            domain=domain,
            groupby="member",
            subplot_title="Member{member}",
            figure_title="{variable_name} over {domain}\nValid time: {valid_time:%H:%M on %-d %B %Y} (T+{lead_time})\n",
        )
        plots = source.map(quickplot_payload)
        return plots
