import json
import os

from IPython.core.display import HTML, display

from mapboxgl.errors import TokenError
from mapboxgl.utils import color_map
from mapboxgl import templates

GL_JS_VERSION = 'v0.44.1'


class MapViz(object):

    def __init__(self,
                 data,
                 access_token=None,
                 center=(0, 0),
                 below_layer='',
                 opacity=1,
                 div_id='map',
                 height='500px',
                 style_url='mapbox://styles/mapbox/light-v9?optimize=true',
                 width='100%',
                 zoom=0,
                 min_zoom=0,
                 max_zoom=24):
        """Construct a MapViz object

        :param data: GeoJSON Feature Collection
        :param access_token: Mapbox GL JS access token.
        :param center: map center point
        :param style_url: url to mapbox style
        :param div_id: The HTML div id of the map container in the viz
        :param width: The CSS width of the HTML div id in % or pixels.
        :param height: The CSS height of the HTML map div in % or pixels.
        :param zoom: starting zoom level for map
        :param opacity: opacity of map data layer

        """
        if access_token is None:
            access_token = os.environ.get('MAPBOX_ACCESS_TOKEN', '')
        if not access_token.startswith('pk'):
            raise TokenError('Mapbox access token must be public (pk). ' \
                             'Please sign up at https://www.mapbox.com/signup/ to get a public token. ' \
                             'If you already have an account, you can retreive your token at https://www.mapbox.com/account/.')
        self.access_token = access_token

        self.template = 'base'
        self.data = data
        self.div_id = div_id
        self.width = width
        self.height = height
        self.style_url = style_url
        self.center = center
        self.zoom = zoom
        self.below_layer = below_layer
        self.opacity = opacity
        self.label_property = None
        self.min_zoom = min_zoom
        self.max_zoom = max_zoom

    def as_iframe(self, html_data):
        """Build the HTML representation for the mapviz."""

        srcdoc = html_data.replace('"', "'")
        return ('<iframe id="{div_id}", srcdoc="{srcdoc}" style="width: {width}; '
                'height: {height};"></iframe>'.format(
                    div_id=self.div_id,
                    srcdoc=srcdoc,
                    width=self.width,
                    height=self.height))

    def show(self, **kwargs):
        # Load the HTML iframe
        html = self.create_html(**kwargs)
        map_html = self.as_iframe(html)

        # Display the iframe in the current jupyter notebook view
        display(HTML(map_html))

    def add_unique_template_variables(self, options):
        pass

    def create_html(self):
        """Create a circle visual from a geojson data source"""
        options = dict(
            gl_js_version=GL_JS_VERSION,
            accessToken=self.access_token,
            div_id=self.div_id,
            styleUrl=self.style_url,
            center=list(self.center),
            zoom=self.zoom,
            geojson_data=json.dumps(self.data, ensure_ascii=False),
            belowLayer=self.below_layer,
            opacity=self.opacity,
            minzoom=self.min_zoom,
            maxzoom=self.max_zoom)

        if self.label_property is None:
            options.update(labelProperty=None)
        else:
            options.update(labelProperty='{' + self.label_property + '}')

        self.add_unique_template_variables(options)

        return templates.format(self.template, **options)


class CircleViz(MapViz):
    """Create a circle map"""

    def __init__(self,
                 data,
                 label_property=None,
                 color_property=None,
                 color_stops=None,
                 color_default='grey',
                 color_function_type='interpolate',
                 *args,
                 **kwargs):
        """Construct a Mapviz object

        :param label_property: property to use for marker label
        :param color_property: property to determine circle color
        :param color_stops: property to determine circle color
        :param color_default: property to determine default circle color if match lookup fails
        :param color_function_type: property to determine `type` used by Mapbox to assign color

        """
        super(CircleViz, self).__init__(data, *args, **kwargs)

        self.template = 'circle'
        self.label_property = label_property
        self.color_property = color_property
        self.color_stops = color_stops
        self.color_function_type = color_function_type
        self.color_default = color_default

    def add_unique_template_variables(self, options):
        """Update map template variables specific to circle visual"""
        options.update(dict(
            geojson_data=json.dumps(self.data, ensure_ascii=False),
            colorProperty=self.color_property,
            colorType=self.color_function_type,
            colorStops=self.color_stops,
            defaultColor=self.color_default
        ))


class GraduatedCircleViz(MapViz):
    """Create a graduated circle map"""

    def __init__(self,
                 data,
                 label_property=None,
                 color_property=None,
                 color_stops=None,
                 color_default='grey',
                 color_function_type='interpolate',
                 radius_property=None,
                 radius_stops=None,
                 radius_default=None,
                 radius_function_type='interpolate',
                 *args,
                 **kwargs):
        """Construct a Mapviz object

        :param label_property: property to use for marker label
        :param color_property: property to determine circle color
        :param color_stops: property to determine circle color
        :param color_default: property to determine default circle color if match lookup fails
        :param color_function_type: property to determine `type` used by Mapbox to assign color
        :param radius_property: property to determine circle radius
        :param radius_stops: property to determine circle radius
        :param radius_default: property to determine default circle radius if match lookup fails
        :param radius_function_type: property to determine `type` used by Mapbox to assign radius size

        """
        super(GraduatedCircleViz, self).__init__(data, *args, **kwargs)

        self.template = 'graduated_circle'
        self.label_property = label_property
        self.color_property = color_property
        self.color_stops = color_stops
        self.radius_property = radius_property
        self.radius_stops = radius_stops
        self.color_function_type = color_function_type
        self.color_default = color_default
        self.radius_function_type = radius_function_type
        self.radius_default = radius_default

    def add_unique_template_variables(self, options):
        """Update map template variables specific to graduated circle visual"""
        options.update(dict(
            colorProperty=self.color_property,
            colorStops=self.color_stops,
            colorType=self.color_function_type,
            radiusType=self.radius_function_type,
            defaultColor=self.color_default,
            defaultRadius=self.radius_default,
            radiusProperty=self.radius_property,
            radiusStops=self.radius_stops,
        ))


class HeatmapViz(MapViz):
    """Create a heatmap viz"""

    def __init__(self,
                 data,
                 weight_property=None,
                 weight_stops=None,
                 color_stops=None,
                 radius_stops=None,
                 *args,
                 **kwargs):
        """Construct a Mapviz object

        :param weight_property: property to determine heatmap weight. EX. "population"
        :param weight_stops: stops to determine heatmap weight.  EX. [[10, 0], [100, 1]]
        :param color_stops: stops to determine heatmap color.  EX. [[0, "red"], [0.5, "blue"], [1, "green"]]
        :param radius_stops: stops to determine heatmap radius based on zoom.  EX: [[0, 1], [12, 30]]

        """
        super(HeatmapViz, self).__init__(data, *args, **kwargs)

        self.template = 'heatmap'
        self.weight_property = weight_property
        self.weight_stops = weight_stops
        self.color_stops = color_stops
        self.radius_stops = radius_stops

    def add_unique_template_variables(self, options):
        """Update map template variables specific to heatmap visual"""
        options.update(dict(
            colorStops=self.color_stops,
            radiusStops=self.radius_stops,
            weightProperty=self.weight_property,
            weightStops=self.weight_stops
        ))


class ClusteredCircleViz(MapViz):
    """Create a clustered circle map"""

    def __init__(self,
                 data,
                 color_stops=None,
                 radius_stops=None,
                 cluster_radius=30,
                 cluster_maxzoom=14,
                 *args,
                 **kwargs):
        """Construct a Mapviz object

        :param color_property: property to determine circle color
        :param color_stops: property to determine circle color
        :param radius_property: property to determine circle radius
        :param radius_stops: property to determine circle radius

        """
        super(ClusteredCircleViz, self).__init__(data, *args, **kwargs)

        self.template = 'clustered_circle'
        self.color_stops = color_stops
        self.radius_stops = radius_stops
        self.clusterRadius = cluster_radius
        self.clusterMaxZoom = cluster_maxzoom

    def add_unique_template_variables(self, options):
        """Update map template variables specific to a clustered circle visual"""
        options.update(dict(
            colorStops=self.color_stops,
            baseColor=self.color_stops[0][1],
            radiusStops=self.radius_stops,
            clusterRadius=self.clusterRadius,
            clusterMaxZoom=self.clusterMaxZoom
        ))


class ChoroplethViz(MapViz):
    """Create a choropleth viz"""

    def __init__(self,
                 data,
                 vector_url=None,
                 vector_layer_name=None,
                 vector_join_property=None,
                 data_join_property=None, # vector only
                 label_property=None,
                 color_property=None,
                 color_stops=None,
                 color_default='grey',
                 color_function_type='interpolate',
                 line_color='white',
                 line_stroke='solid',
                 line_width=1,
                 *args,
                 **kwargs):
        """Construct a Mapviz object

        :param data: can be either GeoJSON (containing polygon features) or JSON for data-join technique with vector polygons
        :param vector_url: optional property to define vector polygon source
        :param vector_layer_name: property to define target layer of vector source
        :param vector_join_property: property to aid in determining color for styling vector polygons
        :param data_join_property: property to join json data to vector features
        :param label_property: property to use for marker label
        :param color_property: property to determine circle color
        :param color_stops: property to determine circle color
        :param color_default: property to determine default circle color if match lookup fails
        :param color_function_type: property to determine `type` used by Mapbox to assign color
        :param line_color: property to determine choropleth line color
        :param line_stroke: property to determine choropleth line stroke (solid, dashed, dotted, dash dot)
        :param line_width: property to determine choropleth line width

        """
        super(ChoroplethViz, self).__init__(data, *args, **kwargs)
        
        self.vector_url = vector_url
        self.vector_layer_name = vector_layer_name
        self.vector_join_property = vector_join_property
        self.data_join_property = data_join_property

        if self.vector_url is not None and self.vector_layer_name is not None:
            self.template = 'vector_choropleth'
            self.vector_source = True
        else:
            self.vector_source = False
            self.template = 'choropleth'

        self.label_property = label_property
        self.color_property = color_property
        self.color_stops = color_stops
        self.color_default = color_default
        self.color_function_type = color_function_type
        self.line_color = line_color
        self.line_stroke = line_stroke
        self.line_width = line_width

    def generate_vector_color_map(self):
        """Generate color stops array for use with match expression in mapbox template"""
        vector_stops = []
        for row in self.data:

            # map color to JSON feature using color_property
            color = color_map(row[self.color_property], self.color_stops, self.color_default)
            
            # link to vector feature using data_join_property (from JSON object)
            vector_stops.append([row[self.data_join_property], color])

        return vector_stops

    def add_unique_template_variables(self, options):
        """Update map template variables specific to heatmap visual"""

        # set line stroke dash interval based on line_stroke property
        if self.line_stroke in ["dashed", "--"]:
            self.line_dash_array = [6, 4]
        elif self.line_stroke in ["dotted", ":"]:
            self.line_dash_array = [0.5, 4]
        elif self.line_stroke in ["dash dot", "-."]:
            self.line_dash_array = [6, 4, 0.5, 4]
        elif self.line_stroke in ["solid", "-"]:
            self.line_dash_array = [1, 0]
        else:
            # default to solid line
            self.line_dash_array = [1, 0]

        # common variables for vector and geojson-based choropleths
        options.update(dict(
            colorStops=self.color_stops,
            colorProperty=self.color_property,
            colorType=self.color_function_type,
            defaultColor=self.color_default,
            lineColor=self.line_color,
            lineDashArray=self.line_dash_array,
            lineStroke=self.line_stroke,
            lineWidth=self.line_width,
        ))

        # vector-based choropleth map variables
        if self.vector_source:
            options.update(dict(
                vectorUrl=self.vector_url,
                vectorLayer=self.vector_layer_name,
                vectorColorStops=self.generate_vector_color_map(),
                vectorJoinColorProperty=self.vector_join_property,
                joinData=json.dumps(self.data, ensure_ascii=False),
                dataJoinProperty=self.data_join_property,
            ))
        
        # geojson-based choropleth map variables
        else:
            options.update(dict(
                geojson_data=json.dumps(self.data, ensure_ascii=False),
            ))

