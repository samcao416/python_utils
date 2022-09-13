C = bpy.context
scn = C.scene

# Get the environment node tree of the current scene
node_tree = scn.world.node_tree
tree_nodes = node_tree.nodes

# Clear all nodes
tree_nodes.clear()

# Add Background node
node_background = tree_nodes.new(type='ShaderNodeBackground')

# Add Environment Texture node
node_environment = tree_nodes.new('ShaderNodeTexEnvironment')
# Load and assign the image to the node property
node_environment.image = bpy.data.images.load("/media/stereye/新加卷/Sam/ambient_image/1_pretville_street_4k.exr") # Relative path
node_environment.location = -300,0

# Add Output node
node_output = tree_nodes.new(type='ShaderNodeOutputWorld')   
node_output.location = 200,0

# Link all nodes
links = node_tree.links
link = links.new(node_environment.outputs["Color"], node_background.inputs["Color"])
link = links.new(node_background.outputs["Background"], node_output.inputs["Surface"])
