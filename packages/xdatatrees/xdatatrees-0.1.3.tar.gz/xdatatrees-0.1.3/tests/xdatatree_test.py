from xdatatrees import (
    xdatatree,
    xfield,
    Attribute,
    Metadata,
    Element,
    TextContent,
    TextElement,
    CamelSnakeConverter,
    SnakeCamelConverter,
    deserialize,
    serialize,
    MetadataNameValue,
    ValueCollector,
    XmlParserOptions,
    TextContentMultipleError,
)


from datatrees import datatree, dtfield

from typing import List, Tuple, Union
import lxml.etree as etree
import numpy as np
import re

from unittest import TestCase, main

# Some example converters just for testing.


@datatree
class GMatrix:
    matrix: np.ndarray = dtfield(doc='The matrix as a numpy array')

    @property
    def A(self):
        return self.matrix

    def __eq__(self, other):
        return np.allclose(self.matrix, other.matrix)


@datatree
class GVector:
    vector: np.ndarray = dtfield(doc='The vector as a numpy array')

    @property
    def A(self):
        return self.vector

    def __eq__(self, other):
        return np.allclose(self.vector, other.vector)


def float_to_str(value: float) -> str:
    """Removes a trailing "." from a floating point number string.
    Args:
      string: A string.
    Returns:
      A string with the trailing "." removed, if it exists.
    """
    string = str(value).rstrip('0')
    if string.endswith('.'):
        return string[:-1]
    else:
        return string


@datatree
class MatrixConverter:
    '''Convert a 16 value string like "1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1" to a
    GMatrix and back.'''

    matrix: GMatrix = dtfield(doc='The matrix as a GMatrix')

    def __init__(self, matrix_str: Union[str, GMatrix]):
        if isinstance(matrix_str, GMatrix):
            self.matrix = matrix_str
        else:
            nparray = np.array([float(x) for x in re.split(r'\s+', matrix_str)])
            self.matrix = GMatrix(nparray.reshape((4, 4)))

    def __str__(self):
        return ' '.join([float_to_str(x) for x in self.matrix.A.flatten()])

    def __repr__(self):
        return self.__str__()


@datatree
class TransformConverter:
    '''Convert a 12 value string like "1 0 0 0 1 0 0 0 1 40 40 10" to a GMatrix
    and back.'''

    matrix: GMatrix = dtfield(doc='The matrix as a GMatrix')

    def __init__(self, matrix_str: Union[str, GMatrix]):
        if isinstance(matrix_str, GMatrix):
            self.matrix = matrix_str
        else:
            nparray = np.array([float(x) for x in re.split(r'\s+', matrix_str)])
            self.matrix = GMatrix(nparray.reshape((3, 4), order='F'))

    def __str__(self):
        nparray = self.matrix.A[0:3].reshape((1, 12), order='F')
        return ' '.join([float_to_str(x) for x in nparray[0]])

    def __repr__(self):
        return self.__str__()


@datatree
class VectorConverter:
    '''Convert a string like "1 2 3" to a GVector and back.'''

    vector: GVector = dtfield(doc='The vector as a GVector')

    def __init__(self, vector_str: Union[str, GVector]):
        if isinstance(vector_str, GVector):
            self.vector = vector_str
        else:
            self.vector = GVector([float(x) for x in re.split(r'\s+', vector_str)])

    def __str__(self):
        return ' '.join([float_to_str(x) for x in self.vector.A[0:3]])

    def __repr__(self):
        return self.__str__()


# Test xdatatree classes.

'''Create a default config for all xdatatree annotationed classes.'''
DEFAULT_CONFIG = xfield(ename_transform=CamelSnakeConverter, ftype=Element)


@xdatatree
class MeshStat:
    XDATATREE_CONFIG = DEFAULT_CONFIG(ftype=Attribute)
    edges_fixed: int = xfield(doc='Number of fixed edges')
    degenerate_facets: int = xfield(doc='Number of degenerate facets')
    facets_removed: int = xfield(doc='Number of facets removed')
    facets_reversed: int = xfield(doc='Number of facets reversed')
    backwards_edges: int = xfield(doc='Number of backwards edges')


@xdatatree
class Part:
    XDATATREE_CONFIG = DEFAULT_CONFIG(ftype=Metadata)
    id: str = xfield(ftype=Attribute, doc='Id of the part')
    subtype: str = xfield(ftype=Attribute, doc='Subtype of the part')
    name: str = xfield(ftype=Metadata, doc='Name of the part')
    matrix: MatrixConverter = xfield(ftype=Metadata, doc='Frame of ref of the object')
    source_file: str
    source_object_id: str
    source_volume_id: str
    source_offset_x: float
    source_offset_y: float
    source_offset_z: float
    mesh_stat: MeshStat = xfield(ftype=Element, doc='Mesh statistics of the part')


@xdatatree
class Object:
    XDATATREE_CONFIG = DEFAULT_CONFIG(ftype=Attribute)
    id: int = xfield(ftype=Attribute, doc='Id of the object')
    name: str = xfield(ftype=Metadata, doc='Name of the object')
    extruder: str = xfield(ftype=Metadata, doc='Name of the object')
    parts: List[Part] = xfield(ftype=Element, doc='List of parts')


@xdatatree
class ModelInstance:
    XDATATREE_CONFIG = DEFAULT_CONFIG(ftype=Metadata)
    object_id: str
    instance_id: str
    identify_id: str


@xdatatree
class Plate:
    XDATATREE_CONFIG = DEFAULT_CONFIG(ftype=Metadata)
    plater_id: str
    plater_name: str
    locked: bool
    thumbnail_file: str
    top_file: str
    pick_file: str
    model_instances: List[ModelInstance] = xfield(
        ename='model_instance', ftype=Element, doc='instances of models on the plate'
    )


@xdatatree
class AssembleItem:
    XDATATREE_CONFIG = DEFAULT_CONFIG(ftype=Attribute)
    object_id: str
    instance_id: str
    transform: TransformConverter
    offset: VectorConverter


@xdatatree
class Assemble:
    XDATATREE_CONFIG = DEFAULT_CONFIG(ftype=Element)
    assemble_items: List[AssembleItem] = xfield(ename='assemble_item', doc='List of assemble items')


@xdatatree
class Config:
    XDATATREE_CONFIG = DEFAULT_CONFIG
    objects: List[Object] = xfield(ename='object', doc='List of objects')
    plate: Plate
    assemble: Assemble


XML_DATA = '''\
<?xml version="1.0" encoding="UTF-8"?>
<config>
  <object id="2">
    <metadata key="name" value="OpenSCAD Model"/>
    <metadata key="extruder" value="2"/>
    <part id="1" subtype="normal_part">
      <metadata key="name" value="OpenSCAD Model"/>
      <metadata key="matrix" value="1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1"/>
      <metadata key="source_file" value="basic_4_model.3mf"/>
      <metadata key="source_object_id" value="0"/>
      <metadata key="source_volume_id" value="0"/>
      <metadata key="source_offset_x" value="40"/>
      <metadata key="source_offset_y" value="40"/>
      <metadata key="source_offset_z" value="10"/>
      <mesh_stat edges_fixed="0" degenerate_facets="0" facets_removed="0" facets_reversed="0" backwards_edges="0"/>
    </part>
  </object>
  <object id="4">
    <metadata key="name" value="OpenSCAD Model"/>
    <metadata key="extruder" value="1"/>
    <part id="3" subtype="normal_part">
      <metadata key="name" value="OpenSCAD Model"/>
      <metadata key="matrix" value="1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1"/>
      <metadata key="source_file" value="basic_4_model.3mf"/>
      <metadata key="source_object_id" value="1"/>
      <metadata key="source_volume_id" value="0"/>
      <metadata key="source_offset_x" value="-20"/>
      <metadata key="source_offset_y" value="40"/>
      <metadata key="source_offset_z" value="10"/>
      <mesh_stat edges_fixed="0" degenerate_facets="0" facets_removed="0" facets_reversed="0" backwards_edges="0"/>
    </part>
  </object>
  <object id="6">
    <metadata key="name" value="OpenSCAD Model"/>
    <metadata key="extruder" value="3"/>
    <part id="5" subtype="normal_part">
      <metadata key="name" value="OpenSCAD Model"/>
      <metadata key="matrix" value="1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1"/>
      <metadata key="source_file" value="basic_4_model.3mf"/>
      <metadata key="source_object_id" value="2"/>
      <metadata key="source_volume_id" value="0"/>
      <metadata key="source_offset_x" value="-20"/>
      <metadata key="source_offset_y" value="-20"/>
      <metadata key="source_offset_z" value="10"/>
      <mesh_stat edges_fixed="0" degenerate_facets="0" facets_removed="0" facets_reversed="0" backwards_edges="0"/>
    </part>
  </object>
  <object id="8">
    <metadata key="name" value="OpenSCAD Model"/>
    <metadata key="extruder" value="4"/>
    <part id="7" subtype="normal_part">
      <metadata key="name" value="OpenSCAD Model"/>
      <metadata key="matrix" value="1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1"/>
      <metadata key="source_file" value="basic_4_model.3mf"/>
      <metadata key="source_object_id" value="3"/>
      <metadata key="source_volume_id" value="0"/>
      <metadata key="source_offset_x" value="40"/>
      <metadata key="source_offset_y" value="-20"/>
      <metadata key="source_offset_z" value="10"/>
      <mesh_stat edges_fixed="0" degenerate_facets="0" facets_removed="0" facets_reversed="0" backwards_edges="0"/>
    </part>
  </object>
  <plate>
    <metadata key="plater_id" value="1"/>
    <metadata key="plater_name" value=""/>
    <metadata key="locked" value="false"/>
    <metadata key="thumbnail_file" value="Metadata/plate_1.png"/>
    <metadata key="top_file" value="Metadata/top_1.png"/>
    <metadata key="pick_file" value="Metadata/pick_1.png"/>
    <model_instance>
      <metadata key="object_id" value="2"/>
      <metadata key="instance_id" value="0"/>
      <metadata key="identify_id" value="463"/>
    </model_instance>
    <model_instance>
      <metadata key="object_id" value="4"/>
      <metadata key="instance_id" value="0"/>
      <metadata key="identify_id" value="483"/>
    </model_instance>
    <model_instance>
      <metadata key="object_id" value="6"/>
      <metadata key="instance_id" value="0"/>
      <metadata key="identify_id" value="503"/>
    </model_instance>
    <model_instance>
      <metadata key="object_id" value="8"/>
      <metadata key="instance_id" value="0"/>
      <metadata key="identify_id" value="523"/>
    </model_instance>
  </plate>
  <assemble>
   <assemble_item object_id="2" instance_id="0" transform="1 0 0 0 1 0 0 0 1 40 40 10" offset="0 0 0" />
   <assemble_item object_id="4" instance_id="0" transform="1 0 0 0 1 0 0 0 1 -20 40 10" offset="0 0 0" />
   <assemble_item object_id="6" instance_id="0" transform="1 0 0 0 1 0 0 0 1 -20 -20 10" offset="0 0 0" />
   <assemble_item object_id="8" instance_id="0" transform="1 0 0 0 1 0 0 0 1 40 -20 10" offset="0 0 0" />
  </assemble>
</config>
'''


class XmlNamespaces:
    '''Helper for namespace definitions for XML.'''

    def __init__(self, xml="http://www.w3.org/XML/1998/namespace", **kwargs):
        self.xml = xml
        self.__dict__.update(kwargs)


NAMESPACES = XmlNamespaces(
    xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02",
    xml="http://www.w3.org/XML/1998/namespace",
    slic3rpe="http://schemas.slic3r.org/3mf/2017/06",
    p="http://schemas.microsoft.com/3dmanufacturing/production/2015/06",
)

DEFAULT_CONFIGX = DEFAULT_CONFIG(xmlns=NAMESPACES.xmlns)
DEFAULT_CONFIG2 = xfield(
    ename_transform=SnakeCamelConverter, aname_transform=SnakeCamelConverter, ftype=Attribute
)
DEFAULT_CONFIG2X = xfield(
    xmlns=NAMESPACES.xmlns,
    ename_transform=SnakeCamelConverter,
    aname_transform=SnakeCamelConverter,
    ftype=Attribute,
)


@xdatatree
class Component:
    XDATATREE_CONFIG = DEFAULT_CONFIGX(ftype=Attribute)
    path: str = xfield(xmlns=NAMESPACES.p, doc='Path of the component')
    objectid: str = xfield(xmlns=None, doc='Object id of the component')
    transform: TransformConverter = xfield(xmlns=None, doc='Transform of the component')


@xdatatree
class Components:
    XDATATREE_CONFIG = DEFAULT_CONFIGX
    components: List[Component] = xfield(ftype=Element, doc='List of components')


@xdatatree
class Vertex:
    x: float = xfield(ftype=Attribute, doc='X coordinate of the vertex')
    y: float = xfield(ftype=Attribute, doc='Y coordinate of the vertex')
    z: float = xfield(ftype=Attribute, doc='Z coordinate of the vertex')

    def get_array(self):
        return np.array([self.x, self.y, self.z])


@xdatatree
class Triangle:
    v1: int = xfield(ftype=Attribute, doc='V1 of the triangle')
    v2: int = xfield(ftype=Attribute, doc='V2 of the triangle')
    v3: int = xfield(ftype=Attribute, doc='V3 of the triangle')
    paint_color: str = xfield(ftype=Attribute, doc='paint_colors of the triangle')

    def get_array(self):
        return np.array([self.v1, self.v2, self.v3])


@datatree
class TriangesCustomConverter(ValueCollector):
    '''A custom converter for a field representing a list of Triange objects.
    This will represent the list of trianges as a numpy array and allow to serialize it
    back to a list of Triange objects.'''

    triangles: List[np.ndarray] = dtfield(default_factory=list, doc='List of vertices')
    paint_colors: List[str] = dtfield(default_factory=list, doc='List of paint colors')

    # This defines is used to read and write the values as xml element.
    CONTAINED_TYPE = Triangle

    def append(self, item: CONTAINED_TYPE):
        if not isinstance(item, self.CONTAINED_TYPE):
            raise ValueError(
                f'Item must be of type {self.CONTAINED_TYPE.__name__} but received {type(item).__name__}'
            )
        self.triangles.append(item.get_array())
        self.paint_colors.append(item.paint_color)

    def get(self):
        return np.array(self.triangles), self.paint_colors

    @classmethod
    def to_contained_type(cls, triangles_paint_colors: Tuple[np.ndarray, List[str]]):
        return (cls.CONTAINED_TYPE(*x[0], paint_color=x[1]) for x in zip(*triangles_paint_colors))


@xdatatree
class Triangles:
    XDATATREE_CONFIG = DEFAULT_CONFIGX
    triangles_paint_colors: List[Tuple[Triangle, List[str]]] = xfield(
        ftype=Element, ename='triangle', builder=TriangesCustomConverter, doc='List of triangles'
    )

    def __eq__(self, __value: object) -> bool:
        return np.array_equal(
            self.triangles_paint_colors[0], __value.triangles_paint_colors[0]
        ) and (self.triangles_paint_colors[1] == __value.triangles_paint_colors[1])


@datatree
class VerticesCustomConverter(ValueCollector):
    '''A custom converter for a field representing a list of Vertex objects.
    This will represent the list of vertices as a numpy array and allow to serialize it
    back to a list of Vertex objects.'''

    vertices: List[np.ndarray] = dtfield(default_factory=list, doc='List of vertices')

    # This defines is used to read and write the values as xml element.
    CONTAINED_TYPE = Vertex

    def append(self, item: CONTAINED_TYPE):
        if not isinstance(item, self.CONTAINED_TYPE):
            raise ValueError(
                f'Item must be of type {self.CONTAINED_TYPE.__name__} but received {type(item).__name__}'
            )
        self.vertices.append(item.get_array())

    def get(self):
        return np.array(self.vertices)

    @classmethod
    def to_contained_type(cls, vertices: np.ndarray):
        return (cls.CONTAINED_TYPE(*x) for x in vertices)


@xdatatree
class Vertices:
    XDATATREE_CONFIG = DEFAULT_CONFIGX
    vertices: np.ndarray = xfield(
        ftype=Element, ename='vertex', builder=VerticesCustomConverter, doc='List of vertices'
    )

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, Vertices):
            return False
        return np.array_equal(self.vertices, __value.vertices)


@xdatatree
class Mesh:
    XDATATREE_CONFIG = DEFAULT_CONFIGX
    vertices: Vertices = xfield(ftype=Element, doc='List of vertices')
    triangles: Triangles = xfield(ftype=Element, doc='List of triangles')


@xdatatree
class Object2:
    XDATATREE_CONFIG = DEFAULT_CONFIGX
    id: int = xfield(ftype=Attribute, xmlns=None, doc='Id of the object')
    uuid: str = xfield(ftype=Attribute, xmlns=NAMESPACES.p, doc='Uuid of the object')
    type: str = xfield(ftype=Attribute, xmlns=None, doc='Type of the object')
    components: List[Components] = xfield(ftype=Element, doc='List of components')
    mesh: Mesh = xfield(ftype=Element, doc='Mesh of the object')


@xdatatree
class Resources:
    XDATATREE_CONFIG = DEFAULT_CONFIGX
    objects: List[Object2] = DEFAULT_CONFIG(ename='object', doc='List of objects')


@xdatatree
class Item:
    XDATATREE_CONFIG = DEFAULT_CONFIGX(ftype=Attribute, xmlns=None)
    objectid: str = xfield(doc='Object id of the item')
    uuid: str = xfield(xmlns=NAMESPACES.p, doc='Uuid of the item')
    transform: TransformConverter = xfield(doc='Transform of the item')
    printable: bool = xfield(doc='Printable of the item')


@xdatatree
class Build:
    XDATATREE_CONFIG = DEFAULT_CONFIGX
    uuid: str = xfield(ftype=Attribute, xmlns=NAMESPACES.p, doc='Uuid of the build')
    items: List[Item] = xfield(doc='List of items')


@xdatatree
class Model:
    XDATATREE_CONFIG = DEFAULT_CONFIG2X(ftype=MetadataNameValue)
    unit: str = xfield(ftype=Attribute, aname='unit', xmlns=None, doc='Unit of the model')
    lang: str = DEFAULT_CONFIG(
        ftype=Attribute, aname='lang', xmlns=NAMESPACES.xml, doc='Language of the model'
    )
    requiredextensions: str = DEFAULT_CONFIG(
        ftype=Attribute, aname='requiredextensions', xmlns=None, doc='Required extensions'
    )
    application: str = xfield(doc='Application creating this model')
    x3mf_content: str = xfield(aname='BambuStudio:3mfVersion', doc='BambuStudio:3mfVersion')
    copyright: str = xfield(aname='CopyRight', doc='The copyright string')
    creation_date: str = xfield(doc='The creation date')
    description: str = xfield(doc='The description string')
    designer: str = xfield(doc='The designer string')
    designer_cover: str = xfield(doc='The designer cover string')
    designer_user_id: str = xfield(doc='The designer user id string')
    license: str = xfield(doc='The license string')
    modification_date: str = xfield(doc='The modification date')
    origin: str = xfield(doc='The origin string')
    title: str = xfield(doc='The title string')
    resources: Resources = xfield(ftype=Element, ename='resources', doc='The resources')
    build: Build = DEFAULT_CONFIGX(ftype=Element, doc='The build')


XML_DATA2 = '''\
<?xml version="1.0" encoding="UTF-8"?>
<model unit="millimeter" xml:lang="en-US" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02" xmlns:slic3rpe="http://schemas.slic3r.org/3mf/2017/06" xmlns:p="http://schemas.microsoft.com/3dmanufacturing/production/2015/06" requiredextensions="p">
 <metadata name="Application">BambuStudio-01.07.04.52</metadata>
 <metadata name="BambuStudio:3mfVersion">1</metadata>
 <metadata name="CopyRight"></metadata>
 <metadata name="CreationDate">2023-09-22</metadata>
 <metadata name="Description"></metadata>
 <metadata name="Designer"></metadata>
 <metadata name="DesignerCover"></metadata>
 <metadata name="DesignerUserId"></metadata>
 <metadata name="License"></metadata>
 <metadata name="ModificationDate">2023-09-22</metadata>
 <metadata name="Origin"></metadata>
 <metadata name="Title"></metadata>
 <resources>
  <object id="2" p:uuid="00000001-61cb-4c03-9d28-80fed5dfa1dc" type="model">
   <components>
    <component p:path="/3D/Objects/OpenSCAD Model_1.model" objectid="1" transform="1 0 0 0 1 0 0 0 1 0 0 0"/>
   </components>
  </object>
  <object id="4" p:uuid="00000002-61cb-4c03-9d28-80fed5dfa1dc" type="model">
   <components>
    <component p:path="/3D/Objects/OpenSCAD Model_2.model" objectid="3" transform="1 0 0 0 1 0 0 0 1 0 0 0"/>
   </components>
  </object>
  <object id="6" p:uuid="00000003-61cb-4c03-9d28-80fed5dfa1dc" type="model">
   <components>
    <component p:path="/3D/Objects/OpenSCAD Model_3.model" objectid="5" transform="1 0 0 0 1 0 0 0 1 0 0 0"/>
   </components>
  </object>
  <object id="8" p:uuid="00000004-61cb-4c03-9d28-80fed5dfa1dc" type="model">
   <components>
    <component p:path="/3D/Objects/OpenSCAD Model_4.model" objectid="7" transform="1 0 0 0 1 0 0 0 1 0 0 0"/>
   </components>
  </object>
 </resources>
 <build p:uuid="d8eb061-b1ec-4553-aec9-835e5b724bb4">
  <item objectid="2" p:uuid="00000002-b1ec-4553-aec9-835e5b724bb4" transform="1 0 0 0 1 0 0 0 1 160.251097 160.519201 10" printable="1"/>
  <item objectid="4" p:uuid="00000004-b1ec-4553-aec9-835e5b724bb4" transform="1 0 0 0 1 0 0 0 1 100.251097 160.519201 10" printable="1"/>
  <item objectid="6" p:uuid="00000006-b1ec-4553-aec9-835e5b724bb4" transform="1 0 0 0 1 0 0 0 1 100.251097 100.519201 10" printable="1"/>
  <item objectid="8" p:uuid="00000008-b1ec-4553-aec9-835e5b724bb4" transform="1 0 0 0 1 0 0 0 1 160.251097 100.519201 10" printable="1"/>
 </build>
</model>
'''

XML_DATA3 = '''\
<?xml version="1.0" encoding="UTF-8"?>
<model unit="millimeter" xml:lang="en-US" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02" xmlns:slic3rpe="http://schemas.slic3r.org/3mf/2017/06" xmlns:p="http://schemas.microsoft.com/3dmanufacturing/production/2015/06" requiredextensions="p">
 <metadata name="BambuStudio:3mfVersion">1</metadata>
 <resources>
  <object id="3" type="model">
   <mesh>
    <vertices>
     <vertex x="-10" y="-10" z="-10"/>
     <vertex x="-10" y="-10" z="10"/>
     <vertex x="-10" y="10" z="-10"/>
     <vertex x="-10" y="10" z="10"/>
     <vertex x="10" y="-10" z="-10"/>
     <vertex x="10" y="-10" z="10"/>
     <vertex x="10" y="10" z="-10"/>
     <vertex x="10" y="10" z="10"/>
    </vertices>
    <triangles>
     <triangle v1="0" v2="1" v3="3"/>
     <triangle v1="0" v2="2" v3="6"/>
     <triangle v1="0" v2="3" v3="2"/>
     <triangle v1="0" v2="4" v3="5" paint_color="4"/>
     <triangle v1="0" v2="5" v3="1" paint_color="4"/>
     <triangle v1="0" v2="6" v3="4"/>
     <triangle v1="1" v2="5" v3="3" paint_color="0C"/>
     <triangle v1="2" v2="3" v3="6"/>
     <triangle v1="3" v2="5" v3="7" paint_color="0C"/>
     <triangle v1="3" v2="7" v3="6"/>
     <triangle v1="4" v2="6" v3="5"/>
     <triangle v1="5" v2="6" v3="7"/>
    </triangles>
   </mesh>
  </object>
 </resources>
</model>
'''

DESERIALIZE_OPTIONS = XmlParserOptions(assert_unused_elements=True, assert_unused_attributes=True)


TEXT_CONTENT_XML = '''\
<text_content_test attr="I'm an attribute">Hello, world!</text_content_test>
'''

@xdatatree
class TextContentTest:
    XDATATREE_CONFIG = DEFAULT_CONFIG
    attr: str = xfield(ftype=Attribute, doc='Attribute')
    text: str = xfield(ftype=TextContent, doc='Text content')

TEXT_ELEMENT_XML = '''\
<text_element_test>
    <title>Hello, world!</title>
    <point>1 2 3</point>
    <point>4 5 6</point>
    <point>7 8 9</point>
</text_element_test>
'''

@xdatatree
class TextElementTest:
    XDATATREE_CONFIG = DEFAULT_CONFIG
    point: List[str] = xfield(ftype=TextElement, doc='Multiple points')
    title: str = xfield(ftype=TextElement, doc='Title')
    

class ExtrudeTest(TestCase):
    
    def testTextContentDefn(self):
        try:
            @xdatatree
            class TextContentTestDupe:
                XDATATREE_CONFIG = DEFAULT_CONFIG
                attr: str = xfield(ftype=Attribute, doc='Attribute')
                text1: str = xfield(ftype=TextContent, doc='Text content')
                text2: str = xfield(ftype=TextContent, doc='Text content')
        except TextContentMultipleError as e:
            self.assertEqual(str(e), 'Only one text content spec is allowed per class.')
        else:
            self.fail('Expected ValueError')
    
    def testTextContent(self):
        xml_tree = etree.fromstring(TEXT_CONTENT_XML.encode('utf-8'))
        text_content_test, status = deserialize(xml_tree, TextContentTest)
        self.assertEqual(text_content_test.text, 'Hello, world!')
        self.assertEqual(text_content_test.attr, "I'm an attribute")
        
        serialized_xml = serialize(text_content_test, 'text_content_test')
        self.assertEqual(serialized_xml.text, 'Hello, world!')
        self.assertEqual(serialized_xml.get('attr'), "I'm an attribute")
    
    def testTextElement(self):
        xml_tree = etree.fromstring(TEXT_ELEMENT_XML.encode('utf-8'))
        text_element_test, status = deserialize(xml_tree, TextElementTest)
        self.assertEqual(text_element_test.title, 'Hello, world!')
        self.assertEqual(text_element_test.point, ['1 2 3', '4 5 6', '7 8 9'])
        
        serialized_xml = serialize(text_element_test, 'text_element_test')
        self.assertEqual(serialized_xml.find('title').text, 'Hello, world!')
        self.assertEqual(serialized_xml.findall('point')[0].text, '1 2 3')
        self.assertEqual(serialized_xml.findall('point')[1].text, '4 5 6')
        self.assertEqual(serialized_xml.findall('point')[2].text, '7 8 9')
        
    def getXml(self):
        return etree.fromstring(XML_DATA.encode('utf-8'))

    def getXml2(self):
        return etree.fromstring(XML_DATA2.encode('utf-8'))

    def getXml3(self):
        return etree.fromstring(XML_DATA3.encode('utf-8'))

    def testXfieldFtypeResolution(self):
        conf = DEFAULT_CONFIG
        conf2 = xfield(ename='object', doc='List of objects')
        conf3 = conf.apply(conf2)

        self.assertEqual(conf3.ftype, Element)
        self.assertEqual(conf3.ename, 'object')

    def testXfield(self):
        conf = xfield(ftype=Attribute)
        conf2 = xfield(ename='object', doc='List of objects')
        conf3 = conf.apply(conf2)

        self.assertEqual(conf3.ftype, Attribute)
        self.assertEqual(conf3.ename, 'object')

    def testDeserialize(self):
        xml_tree = self.getXml()
        config, status = deserialize(xml_tree, Config)

        self.assertEqual(status.contains_unknown_elements, False)
        self.assertEqual(status.contains_unknown_attributes, False)

        self.assertEqual(len(config.objects), 4)

        xml_serialized = serialize(config, 'config', xml_tree.nsmap)

        etree.indent(xml_serialized)
        serialized_string = etree.tostring(xml_serialized)
        # print(serialized_string.decode())

        xml_serialized_from_str = etree.fromstring(serialized_string)

        config2, status = deserialize(xml_serialized_from_str, Config, options=DESERIALIZE_OPTIONS)

        self.assertFalse(status.contains_unknown_elements)
        self.assertFalse(status.contains_unknown_attributes)

        # Testing round trip equivalence.
        self.assertEqual(config, config2)

    def testDeserialize2(self):
        xml_tree = self.getXml2()
        model, status = deserialize(xml_tree, Model)

        self.assertFalse(status.contains_unknown_elements)
        self.assertFalse(status.contains_unknown_attributes)

        self.assertEqual(len(model.build.items), 4)

        xml_serialized = serialize(model, 'model', xml_tree.nsmap)

        etree.indent(xml_serialized)
        serialized_string = etree.tostring(xml_serialized)
        # print(serialized_string.decode())

        xml_serialized_from_str = etree.fromstring(serialized_string)

        model2, status = deserialize(xml_serialized_from_str, Model)

        self.assertFalse(status.contains_unknown_elements)
        self.assertFalse(status.contains_unknown_attributes)

        # Testing round trip equivalence.
        self.assertEqual(model, model2)

    def testDeserialize3(self):
        xml_tree = self.getXml3()
        model, status = deserialize(xml_tree, Model)

        self.assertEqual(status.contains_unknown_elements, False)
        self.assertEqual(status.contains_unknown_attributes, False)

        obj = model.resources.objects[0]
        verts = obj.mesh.vertices.vertices

        self.assertEqual(len(verts), 8)

        xml_serialized = serialize(model, 'model', xml_tree.nsmap)

        etree.indent(xml_serialized)
        serialized_string = etree.tostring(xml_serialized)
        # print(serialized_string.decode())

        xml_serialized_from_str = etree.fromstring(serialized_string)

        model2, status = deserialize(xml_serialized_from_str, Model)

        self.assertFalse(status.contains_unknown_elements)
        self.assertFalse(status.contains_unknown_attributes)

        # Testing round trip equivalence.
        self.assertEqual(model, model2)

    def testMatrixConverter(self):
        value = MatrixConverter("1. 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1")
        value_str = str(value)
        self.assertEqual(value_str, "1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1")

    def testTransformConverter(self):
        value = TransformConverter("1 0 0 0 1 0 0 0 1 40 40 10")
        value_str = str(value)
        self.assertEqual(value_str, "1 0 0 0 1 0 0 0 1 40 40 10")

    def testVectorConverter(self):
        value = VectorConverter("1 2 4")
        value_str = str(value)
        self.assertEqual(value_str, "1 2 4")


if __name__ == "__main__":
    # import sys; sys.argv = ['', 'ExtrudeTest.testDeserialize3']
    main()
