

def clear_scene():
    ###%% clear the scene - Scorch the earth \o/
    import bpy

    print("Clearing scene...")
    try:
        bpy.ops.object.mode_set(mode="OBJECT")
    except:
        pass
    try:
        bpy.ops.object.hide_view_clear()
        bpy.ops.object.select_all(action="SELECT")  # select all objects
        bpy.ops.object.delete(use_global=True)  # delete all objects from all scenes
        bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)
        # Clear data parent collection
        bpy.context.scene.freemocap_properties.data_parent_collection.clear()
        # Clear scene collections
        for collection in bpy.data.collections:
            bpy.data.collections.remove(collection)
    except:
        pass
