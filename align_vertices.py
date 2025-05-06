
bl_info = {
    "name": "Align Vertices",
    "author": "Roderich Vitiysky",
    "version": (1, 0, 0),
    "blender": (3, 0, 0),
    "location": "View3D > N Panel",
    "warning": "",
    "doc_url": "https://github.com/RoderichVitiysky/blender-align-vertices/",
    "category": "Mesh",
    "description":  "Utils to align vertices in edit mode"
}

import bpy
import bmesh
import mathutils
from mathutils import Vector, Matrix

addon_data = {
   't1': -1,
   't2': -1,
   's1': -1,
   's2': -1
}

def addon_execute(context, func, par):
    if context.mode != 'EDIT_MESH':
            return {'CANCELLED'}
    obj = context.active_object
    if obj is None or obj.type != 'MESH':
        self.report({'ERROR'}, "No mesh object selected.")
        return {'CANCELLED'}
    bm = bmesh.from_edit_mesh(obj.data)
    selected_verts = [v for v in bm.verts if v.select]
    result = func(bm, selected_verts, par)
    bmesh.update_edit_mesh(obj.data)
    return result

def select(bm, selected_verts, par):
    if len(selected_verts) < 1:
        addon_data[par] = -1
        return {'CANCELLED'}
    t = selected_verts[0]
    addon_data[par] = selected_verts[0].index
    return {'FINISHED'}

def align_one_point(bm, selected_verts, par):
    if addon_data['t1'] == -1 or addon_data['s1'] == -1:
        return {'CANCELLED'}
    
    translation_vector = bm.verts[addon_data['t1']].co - bm.verts[addon_data['s1']].co
    for vert in selected_verts:
        vert.co += translation_vector
    return {'FINISHED'}

def align_two_point(bm, selected_verts, scale_factor):
    if addon_data['t1'] == -1 or addon_data['t2'] == -1 or addon_data['s1'] == -1 or addon_data['s2'] == -1:
        return {'CANCELLED'}
    
    target_vert1 = bm.verts[addon_data['t1']]
    target_vert2 = bm.verts[addon_data['t2']]
    source_vert1 = bm.verts[addon_data['s1']]
    source_vert2 = bm.verts[addon_data['s2']]

    target_vector = target_vert2.co - target_vert1.co
    source_vector = source_vert2.co - source_vert1.co
    
    target_center = (target_vert1.co + target_vert2.co) / 2
    source_center = (source_vert1.co + source_vert2.co) / 2

    rotation_matrix = source_vector.rotation_difference(target_vector).to_matrix().to_4x4()

    if scale_factor != 1.0:
        source_length = source_vector.length
        target_length = target_vector.length
        
        if source_length == 0:
            scale_factor = 1.0
        else:
            scale_factor = target_length / source_length
    
    for vert in selected_verts:
        original_coords = vert.co.copy()
        translated_coords = original_coords - source_center
        scaled_coords = translated_coords * scale_factor
        rotated_coords = rotation_matrix @ scaled_coords
        final_coords = rotated_coords + target_center
        vert.co = final_coords
    
    return {'FINISHED'}

# ----------------------------------------------------
# UI Elements
# ----------------------------------------------------

class VIEW3D_PT_align_vertices_panel(bpy.types.Panel):
    bl_label = "Align Vertices"
    bl_idname = "VIEW3D_PT_align_vertices"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Align Vertices"

    def draw(self, context):
        layout = self.layout
        layout.operator("object.target1_select", text=f"Target 1 id: {addon_data['t1']:d}")
        layout.operator("object.target2_select", text=f"Target 2 id: {addon_data['t2']:d}")
        layout.separator()
        layout.operator("object.source1_select", text=f"Source 1 id: {addon_data['s1']:d}")
        layout.operator("object.source2_select", text=f"Source 2 id: {addon_data['s2']:d}")
        layout.separator()
        layout.operator("object.align_one_point")
        layout.operator("object.align_two_point")
        layout.operator("object.align_two_point_no_scale")

# ----------------------------------------------------
# Operators
# ----------------------------------------------------

class OBJECT_OT_target1_select(bpy.types.Operator):
    bl_idname = "object.target1_select"
    bl_label = "Select Target 1"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        return addon_execute(context, select, 't1')


class OBJECT_OT_target2_select(bpy.types.Operator):
    bl_idname = "object.target2_select"
    bl_label = "Select Target 2"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        return addon_execute(context, select, 't2')


class OBJECT_OT_source1_select(bpy.types.Operator):
    bl_idname = "object.source1_select"
    bl_label = "Select Source 1"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        return addon_execute(context, select, 's1')


class OBJECT_OT_source2_select(bpy.types.Operator):
    bl_idname = "object.source2_select"
    bl_label = "Select Source 2"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        return addon_execute(context, select, 's2')


class OBJECT_OT_align_one_point(bpy.types.Operator):
    bl_idname = "object.align_one_point"
    bl_label = "Align by 1 Point"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        return addon_execute(context, align_one_point, 0.0)


class OBJECT_OT_align_two_point(bpy.types.Operator):
    bl_idname = "object.align_two_point"
    bl_label = "Align by 2 Points with Scale"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        return addon_execute(context, align_two_point, 0.0)


class OBJECT_OT_align_two_point_no_scale(bpy.types.Operator):
    bl_idname = "object.align_two_point_no_scale"
    bl_label = "Align by 2 Points no Scale"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        return addon_execute(context, align_two_point, 1.0)


# ----------------------------------------------------
# Registration
# ----------------------------------------------------

classes = (
    VIEW3D_PT_align_vertices_panel,
    OBJECT_OT_target1_select,
    OBJECT_OT_target2_select,
    OBJECT_OT_source1_select,
    OBJECT_OT_source2_select,
    OBJECT_OT_align_one_point,
    OBJECT_OT_align_two_point,
    OBJECT_OT_align_two_point_no_scale,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    """
        Usage
        
        Translation
        
        Select vertex then click \"Target 1\"
        Select vertex then click \"Source 1\"
        Translation vector is from source to target
        Select vertices to move then click \"Align by 1 point\"
        Selected vertices will be translated
        
        Translation Rotation and Scaling
        
        Same as first, but also select target 2 and source 2
        Select vertices to move then click \"Align by 2 points\"
        Selected vertices will be translated and scaled and rotated
        
    """
    register()

