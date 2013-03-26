#!/usr/bin/env python

import sys, re, os.path, json
import argparse
from contextlib import contextmanager
import yaml
from collections import defaultdict

# Parcelgen generates parcelable Java classes based
# on a json dictionary of types and properties.  It generates
# a class with the appropriate members and working
# writeToParcel and readFromParcel methods.

# Primary Author: Alex Pretzlav <alex@pretzlav.com>


class ObjectProperty(object):
    """
    A property of an ObjectDescription that includes its name (as returned by the API),
    its type, an optional description, and an optional example value for the property.
    """
    def __init__(self, name, type_, description='', example='', collection=False):
        self.name = name
        self.type_ = type_
        self.description = description
        self.example = example
        self.collection = collection


class ParcelGen:
    BASE_IMPORTS = ("android.os.Parcel", "android.os.Parcelable")
    CLASS_STR = "/* package */ abstract class %s extends %s implements %s"
    CHILD_CLASS_STR = "public class {0} extends _{0} {{"
    NATIVE_TYPES = ["string", "byte", "double", "float", "int", "long", "boolean"]
    NATIVE_OBJECTS = ["String", "Byte", "Double", "Float", "Integer", "Long", "Boolean"]
    JSON_IMPORTS = ["org.json.JSONException", "org.json.JSONObject"]

    tablevel = 0
    outfile = None

    def __init__(self):
        # Lots of default object properties, mostly empty
        self.props = {}
        self.package = 'org.pretz.parcelgen'
        self.do_json = True
        self.imports = []
        self.json_map = {}
        self.default_values = {}
        self.transient = []
        self.extends = "Object"
        self.implements = []
        self.constructors = []
        self.do_json_writer = False
        self.json_blacklist = []
        self.serializables = []
        self.implements = []
        self.from_yaml = False

    def tabify(self, string=''):
        if not string:
            return ''
        return ("\t" * self.tablevel) + string

    @contextmanager
    def indent(self):
        self.uptab()
        yield
        self.downtab()

    @contextmanager
    def block(self, statement='', newline_after=True):
        self.printtab("%s {" % statement)
        with self.indent():
            yield
        self.printtab('}')
        if newline_after:
            self.output()

    def printtab(self, string):
        self.output(self.tabify(string))

    def newline(self, count=1):
        self.output("\n" * (count-1))

    def output(self, string=""):
        if self.outfile:
            self.outfile.write(string + "\n")
        else:
            print string

    def uptab(self):
        self.tablevel += 1

    def downtab(self):
        self.tablevel -= 1

    def memberize(self, name):
        return "m%s%s" % (name[0].capitalize(), name[1:])

    def member_map(self):
        for typ in self.get_types():
            for member in self.props[typ]:
                yield (typ, member)

    def gen_getter(self, typ, member):
        method_name = ""
        if typ == "boolean" and member.startswith("is"):
            method_name = member
        else:
            method_name = "get%s%s" % (member[0].capitalize(), member[1:])
        return "\tpublic %s %s() {\n\t\t return %s;\n\t}" % (typ, method_name, self.memberize(member))
        
    def gen_setter(self, typ, member):
        method_name = ""
        if typ == "boolean" and member.startswith("is"):
            method_name = member
        else:
            method_name = "set%s%s" % (member[0].capitalize(), member[1:])
        return "\tpublic void %s(%s %s) {\n\t\t this.%s = %s;\n\t}" % (method_name, typ, member, self.memberize(member), member)

    def list_type(self, typ):
        match = re.match(r"(List|ArrayList)<(.*)>", typ)
        if match:
            return match.group(2)
        return None

    def gen_list_parcelable(self, typ, memberized):
        classname = self.list_type(typ)
        if not classname:
            return None
        elif classname == "String":
            return self.tabify("parcel.writeStringList(%s);" % memberized)
        else:
            if self.list_type(typ) in self.NATIVE_OBJECTS:
                return self.tabify("parcel.writeSerializable(%s);" % memberized)
            else:
                return self.tabify("parcel.writeTypedList(%s);" % memberized)

    def gen_list_unparcel(self, typ, memberized):
        classname = self.list_type(typ)
        if not classname:
            return None
        if (classname == "String"):
            return self.tabify("%s = source.createStringArrayList();" % memberized)
        else:
            if self.list_type(typ) in self.NATIVE_OBJECTS:
                return self.tabify("%s = (ArrayList<%s>) source.readSerializable();" % (memberized, classname))
            else:
                return self.tabify("%s = source.createTypedArrayList(%s.CREATOR);" % (memberized, classname))

    def gen_parcelable_line(self, typ, member):
        memberized = self.memberize(member)
        if typ in self.NATIVE_TYPES:
            return self.tabify("parcel.write%s(%s);" % (typ.capitalize(), memberized))
        elif typ in self.NATIVE_OBJECTS:
            return self.tabify("parcel.writeValue(%s);" % memberized)
        elif typ == "Date":
            return self.tabify("parcel.writeLong(%s == null ? Integer.MIN_VALUE : %s.getTime());" % (
                memberized, memberized))
        elif self.list_type(typ):
            return self.gen_list_parcelable(typ, memberized)
        elif typ in self.serializables:
            return self.tabify("parcel.writeSerializable(%s);" % memberized)
        else:
            return self.tabify("parcel.writeParcelable(%s, 0);" % memberized)

    def get_types(self):
        types = self.props.keys()
        types.sort()
        return types

    def gen_parcelable(self):
        result = ""
        if self.extends != "Object":
            result += self.tabify("super.writeToParcel(parcel, flags);\n");
        for typ in self.get_types():
            if typ == "boolean":
                joined = ", ".join(map(self.memberize, self.props[typ]))
                result += self.tabify("parcel.writeBooleanArray(new boolean[] {%s});\n" % joined)
            else:
                for member in self.props[typ]:
                    result += self.gen_parcelable_line(typ, member) + "\n"
        return result[:-1] # Strip last newline because I'm too lazy to do this right

    def print_creator(self, class_name, parcel_class, close=True):
        # Simple parcelable creator that uses readFromParcel
        self.printtab("public static final {0}<{1}> CREATOR = new {0}<{1}>() {{".format(
                 parcel_class, class_name))
        self.uptab()
        self.newline()
        self.printtab("public {0}[] newArray(int size) {{\n{1}return new {0}[size];\n\t\t}}".format(
            class_name, "\t" * (self.tablevel + 1)))
        self.newline()
        self.printtab("public %s createFromParcel(Parcel source) {" % class_name)
        self.uptab()
        self.printtab("{0} object = new {0}();".format(class_name))
        self.printtab("object.readFromParcel(source);")
        self.printtab("return object;")
        self.downtab()
        self.printtab("}")
        if close:
            self.downtab()
            self.printtab("};\n")
            self.downtab()

    def print_child(self, child_name, package, other_imports, constructors):
        self.tablevel = 0
        self.printtab("package %s;\n" % package)
        imports = ["android.os.Parcel"]
        imports.extend(other_imports)
        if self.do_json:
            imports.extend(self.JSON_IMPORTS)
            imports.append("com.yelp.parcelgen.JsonParser.DualCreator")
        else:
            imports.append("android.os.Parcelable")
        for import_string in imports:
            self.printtab("import %s;" % import_string)
        self.newline(2)
        self.printtab(self.CHILD_CLASS_STR.format(child_name))
        self.newline()
        self.uptab()
        
        # User-defined constructors
        for c in constructors:
            constructor = "public %s(" % child_name
            params = []
            values = []
            
            for item in c["args"]:
                params.append("%s %s" % (item[0], item[1]))
                values.append(item[1])
                
            if c.get("throws", None):
                constructor += "%s) throws %s {" %(", ".join(params), ", ".join(c.get("throws")))
            else:
                constructor += "%s) {" % (", ".join(params))
            
            self.printtab(constructor)
            self.uptab()        
            self.printtab("super(%s);" % ", ".join(values))
            self.downtab()
            self.printtab("}\n")
        
        if self.do_json:
            self.print_creator(child_name, "DualCreator", False)
            self.newline()
            self.printtab("@Override")
            self.printtab("public %s parse(JSONObject obj) throws JSONException {" % child_name)
            self.uptab()
            self.printtab("{0} newInstance = new {0}();".format(child_name))
            self.printtab("newInstance.readFromJson(obj);")
            self.printtab("return newInstance;")
            self.downtab()
            self.printtab("}\n\t};\n")
            self.downtab()
        else:
            self.print_creator(child_name, "Parcelable.Creator")
        self.downtab()
        self.printtab("}")

    def needs_jsonutil(self):
        if "Date" in self.props:
            return True
        for key in self.props.keys():
            if "List" in key:
                return True
        return False

    def print_gen(self, class_name):
        self.tablevel = 0
        for line in self.generate_class(class_name):
            # TODO: Make this a nice regex
            if line and not (line.endswith(';') or line.endswith('{') or 
                line.endswith('\n') or line.startswith('/*') or line.startswith(' *')):
                line += ';'
            self.printtab(line)

    def generate_class(self, class_name):
        # Imports and open class definition
        yield "package %s;\n" % self.package
        imports = set(tuple(self.imports) + self.BASE_IMPORTS)
        for prop in self.props.keys():
            if prop.startswith("List"):
                imports.add("java.util.List")
            elif prop.startswith("ArrayList"):
                imports.add("java.util.ArrayList")
            elif prop == "Date":
                imports.add("java.util.Date")
            elif prop == "Uri":
                imports.add("android.net.Uri")

        if self.do_json:
            imports.update(self.JSON_IMPORTS)
            if self.needs_jsonutil():
                imports.add("com.yelp.parcelgen.JsonUtil")
        if 'Serializable' in self.implements:
            imports.add("java.io.Serializable")
        imports = list(imports)
        imports.sort()

        for imp in imports:
            yield "import %s;" % imp

        self.output("")
        yield "/** Automatically generated Parcelable implementation for %s." % class_name
        yield " *    DO NOT MODIFY THIS FILE MANUALLY! IT WILL BE OVERWRITTEN THE NEXT TIME"
        yield " *    %s's PARCELABLE DESCRIPTION IS CHANGED." % class_name
        yield " */"

        implements = ", ".join(['Parcelable'] + self.implements)
        with self.block(self.CLASS_STR % (class_name, self.extends, implements), newline_after=False):
            yield
            # Protected member variables
            for typ, member in self.member_map():
                if member in self.transient:
                    typ = "transient " + typ
                yield "protected %s %s;" % (typ, self.memberize(member))
            yield

            #If the user didn't define any constructors, put in parameterized and empty constructors
            if not self.constructors:
                # Parameterized Constructor
                constructor = "protected %s(" % class_name
                params = []
                for typ, member in self.member_map():
                    params.append("%s %s" % (typ, member))
                constructor += "%s)" % ", ".join(params)
                with self.block(constructor):
                    yield "this();"
                    for typ, member in self.member_map():
                        yield "%s = %s;" % (self.memberize(member), member)
                
                # Empty constructor for Parcelable
                with self.block("protected %s()" % class_name):
                    yield "super();"

            # User-defined constructors
            for c in self.constructors:
                constructor = "protected %s(" % class_name
                params = []
                values = []
                
                for item in c["args"]:
                    params.append("%s %s" % (item[0], item[1]))
                    values.append(item[1])
                    
                if c.get("throws", None):
                    constructor += "%s) throws %s" %(", ".join(params), ", ".join(c.get("throws")))
                else:
                    constructor += "%s)" % (", ".join(params))
                
                with self.block(constructor):
                    yield "super(%s)" % ", ".join(values)
        
            # Getters for member variables
            for typ, member in self.member_map():
                self.output(self.gen_getter(typ, member))
                yield
                self.output(self.gen_setter(typ, member))
                yield
            yield

            # Parcelable writeToParcel
            with self.block("public int describeContents()"):
                yield 'return 0'
            
            with self.block("public void writeToParcel(Parcel parcel, int flags)"):
                self.output(self.gen_parcelable())

            # readFromParcel that allows subclasses to use parcelable-ness of their superclass
            with self.block("public void readFromParcel(Parcel source)"):
                i = 0
                all_members = []
                if self.extends != "Object":
                    yield "super.readFromParcel(source)"
                for typ in self.get_types():
                    if typ == "boolean":
                        yield "boolean[] bools = source.createBooleanArray()"
                        for j in xrange(len(self.props[typ])):
                            yield "%s = bools[%d]" % (self.memberize(self.props[typ][j]), j)
                    else:
                        for member in self.props[typ]:
                            memberized = self.memberize(member)
                            list_gen = self.gen_list_unparcel(typ, memberized)
                            if list_gen:
                                self.output(list_gen)
                            elif typ == "Date":
                                yield "long date%d = source.readLong()" % i
                                with self.block("if (date%d != Integer.MIN_VALUE)" % i):
                                    yield "%s = new Date(date%d)" % (memberized, i)
                                    i += 1
                            elif typ in self.NATIVE_TYPES:
                                yield "%s = source.read%s()" % (memberized, typ.capitalize())
                            elif typ in self.NATIVE_OBJECTS:
                                yield "%s = (%s) source.readValue(%s.class.getClassLoader())" % (memberized, typ, typ)
                            elif typ in self.serializables:
                                yield "%s = (%s)source.readSerializable()" % (memberized, typ)
                            else:
                                yield "%s = source.readParcelable(%s.class.getClassLoader())" % (memberized, typ)
    #       self.print_creator(class_name, "Parcelable.Creator")

            if self.do_json:
                self.output(self.generate_json_reader(self.props))
            if self.do_json_writer:
                self.output(self.generate_json_writer(self.props))

    def generate_json_reader(self, props):
        self.props = props
        fun = self.tabify("public void readFromJson(JSONObject json) throws JSONException {\n")
        self.uptab()
        # Parcelable doesn't support boolean without help, JSON does
        NATIVES = self.NATIVE_TYPES + ["boolean"]
        for typ in self.get_types():
            list_type = self.list_type(typ)
            # Always protect strings with isNull check because JSONObject.optString()
            # returns the string "null" for null strings.    AWESOME.
            protect = typ not in [native for native in NATIVES if native != "String"]
            for member in props[typ]:
                newline = True
                # Some object members are derived and not stored in JSON
                if member in self.json_blacklist:
                    continue
                # Some members have different names in JSON
                if member in self.json_map:
                    key = self.json_map[member]
                else:
                    key = camel_to_under(member)
                # Need to check if key is defined if we have a default value too
                if member in self.default_values:
                    protect = True
                if protect:
                    fun += self.tabify("if (!json.isNull(\"%s\")) {\n" % key)
                    self.uptab()
                fun += self.tabify("%s = " % self.memberize(member))
                if typ.lower() == "float":
                    fun += "(float)json.optDouble(\"%s\")" % key
                elif typ.lower() in NATIVES:
                    fun += "json.opt%s(\"%s\")" % (typ.capitalize(), key)
                elif typ == "Integer":
                    fun += "json.optInt(\"%s\")" % key
                elif typ == "List<String>":
                    fun += "JsonUtil.getStringList(json.optJSONArray(\"%s\"))" % key
                elif typ == "Date":
                    fun += "JsonUtil.parseTimestamp(json, \"%s\")" % key
                elif typ == "Uri":
                    fun += "Uri.parse(json.getString(\"%s\"))" % key
                elif list_type:
                    if list_type in self.NATIVE_OBJECTS:
                        newline = False
                        listmatcher = re.match(r"(?P<list_type>Array)?List(?P<content_type>[<>a-zA-Z0-9_]*)", typ)
                        if listmatcher is not None:
                            match_dict = listmatcher.groupdict()
                            if match_dict['list_type'] is not None and match_dict['content_type'] is not None:
                                fun += ("new %sList%s()" % (match_dict['list_type'], match_dict['content_type']))
                            else:
                                fun += "java.util.Collections.emptyList()"
                            fun += ";\n"
                        fun += self.tabify("JSONArray tmpArray = json.optJSONArray(\"%s\");\n" % key)
                        fun += self.tabify("if (tmpArray != null) {\n")
                        self.uptab()
                        fun += self.tabify("for (int i=0; i<tmpArray.length(); i++) {\n")
                        self.uptab()
                        fun += self.tabify("%s.add((%s) tmpArray.get(i));\n" % (self.memberize(member), list_type))
                        self.downtab()
                        fun += self.tabify("}\n")
                        self.downtab()
                        fun += self.tabify("}\n")
                    else:
                        fun += "JsonUtil.parseJsonList(json.optJSONArray(\"%s\"), %s.CREATOR)" % (key, list_type)
                else:
                    fun += "%s.CREATOR.parse(json.getJSONObject(\"%s\"))" % (typ, key)
                if newline:
                    fun += ";\n"
                if protect:
                    self.downtab()
                    listmatcher = re.match(r"(?P<list_type>Array)?List(?P<content_type>[<>a-zA-Z0-9_]*)", typ)
                    if listmatcher is not None:
                        match_dict = listmatcher.groupdict()
                        fun += self.tabify("} else {\n")
                        self.uptab()
                        fun += self.tabify(("%s = " % self.memberize(member)))
                        if match_dict['list_type'] is not None and match_dict['content_type'] is not None:
                            fun += ("new %sList%s()" % (match_dict['list_type'], match_dict['content_type']))
                        else:
                            fun += "java.util.Collections.emptyList()"
                        fun += ";\n"
                        self.downtab()
                    elif member in self.default_values:
                        fun += self.tabify("} else {\n")
                        self.uptab()
                        fun += self.tabify(("%s = %s;\n" % (self.memberize(member), self.default_values[member])))
                        self.downtab()
                    fun += self.tabify("}\n")
        self.downtab()
        fun += self.tabify("}\n")
        return fun

    def generate_json_writer(self, foo):
        fun = self.tabify("public JSONObject writeJSON() throws JSONException {\n")
        self.uptab()
        fun += self.tabify("JSONObject json = new JSONObject();\n")
        # Parcelable doesn't support boolean without help, JSON does
        NATIVES = self.NATIVE_TYPES + ["boolean", "String"]
        for typ in self.get_types():
            list_type = self.list_type(typ)
            # Always protect strings with isNull check because JSONObject.optString()
            # returns the string "null" for null strings.    AWESOME.
            protect = typ not in [native for native in NATIVES if native != "String"]
            for member in self.props[typ]:
                # Some object members are derived and not stored in JSON
                if member in self.json_blacklist:
                    continue
                # Some members have different names in JSON
                if member in self.json_map:
                    key = self.json_map[member]
                else:
                    key = camel_to_under(member)
                if protect:
                    fun += self.tabify("if (%s != null) {\n" % self.memberize(member))
                    self.uptab()
                if typ == "List<String>":
                    fun += self.tabify("// TODO list writing %s\n" % self.memberize(member))
                elif typ == "Date":
                    fun += self.tabify("json.put(\"%s\", %s.getTime() / 1000);\n" % (key, self.memberize(member)))
                elif typ == "Uri":
                    fun += self.tabify("json.put(\"%s\", String.valueOf(%s));\n" % (key, self.memberize(member)))
                elif list_type:
                    fun += self.tabify("// TODO LIST writing %s \n" % self.memberize(member))
                elif typ in NATIVES:
                    fun += self.tabify("json.put(\"%s\", %s);\n" % (key, self.memberize(member)))
                else:
                    fun += self.tabify("json.put(\"%s\", %s.writeJSON());\n" % (key, self.memberize(member)))
                if protect:
                    self.downtab()
                    fun += self.tabify("}\n")
        fun += self.tabify("return json;\n")
        self.downtab()
        fun += self.tabify("}\n")
        return fun


def camel_to_under(member):
    """ Convert NamesInCamelCase to jsonic_underscore_names"""
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', member)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

def under_to_camel(member):
    """ Convert jsonic_underscore_names to namesInCamelCase"""
    def upper(match):
        return match.group(1).upper()
    return re.sub('_([a-z0-9])', upper, member)

def config_prop(dic, keypath, default=''):
    paths = keypath.split('.')
    for entry in paths:
        if entry in dic:
            dic = dic[entry]
        else:
            return default
    return dic

def read_json(file_path):
    """
    Returns a ParcelGen generator configured for the
    the object described by the json file at file_path.
    """
    with open(file_path, 'rU') as json_file:
        description = json.load(json_file)
    generator = ParcelGen()
    generator.props = description.get("props") or {}
    generator.package = description.get("package") or None
    imports = description.get("imports") or ()
    json_map = description.get("json_map") or {}
    default_values = description.get("default_values") or {}
    transient = description.get("transient") or []
    make_serializable = description.get("make_serializable")
    do_json_writer = description.get("do_json_writer")
    json_blacklist = description.get("json_blacklist") or []
    serializables = description.get("serializables") or ()
    if 'do_json' in description:
        do_json = description.get("do_json")
    else:
        do_json = True
    # object_properties = []
    # for type_, values in generator.props.iteritems():
    #     for name in values:
    #         object_properties.append(ObjectProperty(name, type_))

    extends = description.get("extends") or "Object"    
    constructors = description.get("constructors") or []

    generator.json_map = json_map
    generator.json_blacklist = json_blacklist
    generator.serializables = serializables
    generator.do_json = do_json
    generator.do_json_writer = do_json_writer
    generator.extends = extends
    generator.constructors = constructors
    if make_serializable:
        generator.implements = ['Serializable']
    else:
        generator.implements = []
    generator.default_values = default_values
    return generator


def read_yaml(file_path, config_file):
    yaml_to_java_types = {
        'Integer': 'int',
        'Boolean': 'boolean',
        'Float': 'float',
        'Long': 'long',
        'Double': 'double',
        'Url': 'Uri'
    }
    def process_yaml_node(typ, values):
        typ = yaml_to_java_types.get(typ, typ)
        if isinstance(values, dict):
            for name, meta in values.iteritems():
                if isinstance(meta, basestring):
                    yield ObjectProperty(name, typ, description=meta)
                else:
                    yield ObjectProperty(name, typ, description=meta.get('desc'), example=meta.get('ex'))
        else:
            yield ObjectProperty(name, typ)
    with open(file_path, 'rU') as yaml_file:
        description = yaml.safe_load(yaml_file)
    object_properties = []
    for type_, values in description.iteritems():
        if isinstance(values, dict):
            object_properties.extend(process_yaml_node(type_, values))
        else:
            for value in values:
                object_properties.extend(process_yaml_node(type_, value))
    object_name = os.path.basename(file_path).split(".")[0]
    generator = ParcelGen()
    generator.from_yaml = True
    # Defaults to be overridden by config file
    rename = {}
    if (config_file):
        with open(config_file, 'rU') as yaml_config:
            config = yaml.safe_load(yaml_config)
        generator.package = config_prop(
            config,
            'Target.default_package',
            default=generator.package)
        obj_config = config.get('Config', {}).get(object_name, None)
        if obj_config:
            rename = obj_config.get('rename', rename)
            generator.implements = obj_config.get('implement', [])
            generator.transient.extend(obj_config.get('transient', []))
            generator.extends = obj_config.get('extends', generator.extends)
            generator.constructors = obj_config.get('constructors', generator.constructors)
            for prop in ['do_json_writer', 'serializables', 'json_blacklist', 'default_values', 'imports', 'package']:
                if prop in obj_config:
                    setattr(generator, prop, obj_config[prop])
    # TODO: invert this and pass object properties into generator
    props = defaultdict(list)
    json_map = {}
    for object_prop in object_properties:
        type_ = object_prop.type_
        if type_.endswith('[]'):
            type_ = "ArrayList<%s>" % type_[:-2]
        if object_prop.name in rename:
            name = rename[object_prop.name]
        else:
            name = under_to_camel(object_prop.name)
        json_map[name] = object_prop.name
        props[type_].append(name)
    # For compatibility, json_map contains every ivar->json mapping
    generator.json_map = json_map
    generator.props = props
    return generator


def generate_class(filePath, output, config=None):
    # Read parcelable description json
    if filePath.endswith('json'):
        generator = read_json(filePath)
    elif filePath.endswith('yaml'):
        generator = read_yaml(filePath, config)
    else:
        raise Exception("Unsupported file type: %s" % filePath)
    class_name = "_" + os.path.basename(filePath).split(".")[0]

    if output:
        package = generator.package
        if (os.path.isdir(output)): # Resolve file location based on package + path
            dirs = package.split(".")
            dirs.append(class_name + ".java")
            targetFile = os.path.join(output, *dirs)
            # Generate child subclass if it doesn't exist
            if class_name.startswith("_"):
                child = class_name[1:]
                new_dirs = package.split(".")
                new_dirs.append(child + ".java")
                child_file = os.path.join(output, *new_dirs)
                if not os.path.exists(child_file):
                    generator.outfile = open(child_file, 'w')
                    generator.print_child(child, package)
        else:
            targetFile = output
        generator.outfile = open(targetFile, 'w')
    generator.print_gen(class_name)


if __name__ == "__main__":
    usage = """
Generates a parcelable Java implementation for provided description file.
Writes to stdout unless destination is specified.

If destination is a directory, it is assumed to be the top level
directory of your Java source. Your class file will be written in the
appropriate folder based on its Java package.
If destination is a file, your class will be written to that file."""
    parser = argparse.ArgumentParser(description=usage)
    parser.add_argument('parcelfile', help='The parcelable file or a directory of files to generate source from')
    parser.add_argument('-c', '--config', help='Yaml config file to use while generating source code')
    parser.add_argument('destination', nargs='?', help='Output file or directory for ' + 
        'generated files, outputs to stdout if unspecified')
    args = parser.parse_args()
    source = args.parcelfile
    destination = args.destination

    # If both source and destination are directories, run in
    # fake make mode 
    if (os.path.isdir(source) and os.path.isdir(destination)):
        for sourcefile in [sourcefile for sourcefile in os.listdir(source) if sourcefile.endswith(".json")]:
            print "Using source and target directories is deprecated. Write a makefile (see example app)."
            print "decoding ", sourcefile
            generate_class(os.path.join(source, sourcefile), destination)
    else:
        generate_class(source, destination, config=args.config)

