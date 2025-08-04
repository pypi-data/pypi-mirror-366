"""
Sandbox to VRM Converter
Handles conversion of Sandbox avatar files (.glb, .vox) to VRM 1.0 format
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

import numpy as np
from pygltflib import GLTF2, Accessor, BufferView, Buffer, Scene, Node, Mesh, Primitive, Material
from PIL import Image
import trimesh

# Configure logging
logger = logging.getLogger(__name__)

class SandboxToVRMConverter:
    """Converts Sandbox avatars to VRM 1.0 format"""
    
    def __init__(self):
        self.vrm_extension_template = {
            "extensionsUsed": ["VRM"],
            "extensions": {
                "VRM": {
                    "meta": {
                        "title": "Sandbox Avatar",
                        "version": "1.0",
                        "author": "Avatar Everywhere",
                        "contactInformation": "",
                        "reference": "",
                        "allowedUserName": "Everyone", 
                        "violentUsage": "Disallow",
                        "sexualUsage": "Disallow",
                        "commercialUsage": "Allow",
                        "otherPermissionUrl": "",
                        "licenseName": "Other",
                        "otherLicenseUrl": ""
                    },
                    "humanoid": {
                        "humanBones": []
                    },
                    "firstPerson": {
                        "firstPersonBone": -1,
                        "firstPersonBoneOffset": {
                            "x": 0.0,
                            "y": 0.0,
                            "z": 0.0
                        },
                        "meshAnnotations": []
                    },
                    "blendShapeMaster": {
                        "blendShapeGroups": []
                    },
                    "secondaryAnimation": {
                        "boneGroups": [],
                        "colliderGroups": []
                    },
                    "materialProperties": []
                }
            }
        }
    
    def convert(self, input_file: Path, output_file: Path) -> bool:
        """Main conversion method"""
        try:
            logger.info(f"Starting conversion: {input_file} -> {output_file}")
            
            if input_file.suffix.lower() == '.glb':
                return self._convert_glb_to_vrm(input_file, output_file)
            elif input_file.suffix.lower() == '.vox':
                return self._convert_vox_to_vrm(input_file, output_file)
            else:
                raise ValueError(f"Unsupported file format: {input_file.suffix}")
        except Exception as e:
            logger.error(f"Conversion error: {e}")
            return False
    
    def analyze_glb(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Analyze GLB file and return metadata"""
        try:
            logger.info(f"Analyzing GLB file: {file_path}")
            gltf = GLTF2.load(file_path)
            
            info = {
                'mesh_count': len(gltf.meshes) if gltf.meshes else 0,
                'material_count': len(gltf.materials) if gltf.materials else 0,
                'texture_count': len(gltf.textures) if gltf.textures else 0,
                'has_skeleton': bool(gltf.skins),
                'node_count': len(gltf.nodes) if gltf.nodes else 0
            }
            
            logger.info(f"GLB analysis complete: {info}")
            return info
        except Exception as e:
            logger.error(f"Error analyzing GLB: {e}")
            return None
    
    def _convert_glb_to_vrm(self, input_file: Path, output_file: Path) -> bool:
        """Convert GLB file to VRM format"""
        try:
            # Load the GLB file
            gltf = GLTF2.load(input_file)
            
            # Add VRM extension
            if not hasattr(gltf, 'extensions') or gltf.extensions is None:
                gltf.extensions = {}
            
            # Copy VRM extension template
            gltf.extensions.update(self.vrm_extension_template["extensions"])
            
            # Add VRM to extensionsUsed
            if not hasattr(gltf, 'extensionsUsed') or gltf.extensionsUsed is None:
                gltf.extensionsUsed = []
            
            if "VRM" not in gltf.extensionsUsed:
                gltf.extensionsUsed.append("VRM")
            
            # Set up basic humanoid bones if skeleton exists
            if gltf.skins and len(gltf.skins) > 0:
                self._setup_basic_humanoid_bones(gltf)
            
            # Set up material properties
            if gltf.materials:
                self._setup_vrm_materials(gltf)
            
            # Update metadata
            avatar_name = input_file.stem
            gltf.extensions["VRM"]["meta"]["title"] = f"Sandbox Avatar - {avatar_name}"
            
            # Save as VRM
            gltf.save(output_file)
            return True
            
        except Exception as e:
            print(f"GLB conversion error: {e}")
            return False
    
    def _convert_vox_to_vrm(self, input_file: Path, output_file: Path) -> bool:
        """Convert VOX file to VRM format"""
        try:
            # For VOX files, we need to convert to mesh first
            # This is a simplified implementation - in production you'd want a proper VOX parser
            
            # Load as mesh using trimesh (may not work directly with .vox)
            try:
                mesh = trimesh.load(input_file)
            except Exception:
                print("Error: VOX file format not directly supported. Please export as GLB from VoxEdit first.")
                return False
            
            # Create a basic GLTF structure
            gltf = GLTF2()
            
            # Convert mesh to GLTF format
            vertices = mesh.vertices.astype(np.float32)
            faces = mesh.faces.flatten().astype(np.uint32)
            
            # Create buffers, buffer views, and accessors
            vertex_buffer = vertices.tobytes()
            index_buffer = faces.tobytes()
            
            # Combine buffers
            total_buffer = vertex_buffer + index_buffer
            
            # Create GLTF components
            buffer = Buffer(byteLength=len(total_buffer), uri=None)
            gltf.buffers = [buffer]
            
            # Vertex buffer view
            vertex_buffer_view = BufferView(
                buffer=0,
                byteOffset=0,
                byteLength=len(vertex_buffer),
                target=34962  # ARRAY_BUFFER
            )
            
            # Index buffer view  
            index_buffer_view = BufferView(
                buffer=0,
                byteOffset=len(vertex_buffer),
                byteLength=len(index_buffer),
                target=34963  # ELEMENT_ARRAY_BUFFER
            )
            
            gltf.bufferViews = [vertex_buffer_view, index_buffer_view]
            
            # Position accessor
            position_accessor = Accessor(
                bufferView=0,
                byteOffset=0,
                componentType=5126,  # FLOAT
                count=len(vertices),
                type="VEC3",
                max=vertices.max(axis=0).tolist(),
                min=vertices.min(axis=0).tolist()
            )
            
            # Index accessor
            index_accessor = Accessor(
                bufferView=1,
                byteOffset=0,
                componentType=5125,  # UNSIGNED_INT
                count=len(faces),
                type="SCALAR"
            )
            
            gltf.accessors = [position_accessor, index_accessor]
            
            # Create primitive
            primitive = Primitive(
                attributes={"POSITION": 0},
                indices=1
            )
            
            # Create mesh
            mesh_obj = Mesh(primitives=[primitive])
            gltf.meshes = [mesh_obj]
            
            # Create node
            node = Node(mesh=0)
            gltf.nodes = [node]
            
            # Create scene
            scene = Scene(nodes=[0])
            gltf.scenes = [scene]
            gltf.scene = 0
            
            # Add VRM extension
            gltf.extensions = self.vrm_extension_template["extensions"].copy()
            gltf.extensionsUsed = ["VRM"]
            
            # Update metadata
            avatar_name = input_file.stem
            gltf.extensions["VRM"]["meta"]["title"] = f"Sandbox Avatar - {avatar_name}"
            
            # Save with binary data
            gltf.set_binary_blob(total_buffer)
            gltf.save(output_file)
            
            return True
            
        except Exception as e:
            print(f"VOX conversion error: {e}")
            return False
    
    def _setup_basic_humanoid_bones(self, gltf: GLTF2):
        """Set up basic humanoid bone mapping"""
        # This is a simplified bone mapping - in production you'd want more sophisticated bone detection
        
        humanoid_bones = []
        
        if gltf.nodes:
            # Try to find common bone names
            bone_mapping = {
                "hips": ["hips", "pelvis", "root"],
                "spine": ["spine", "spine1"],
                "chest": ["chest", "spine2", "upper_torso"],
                "neck": ["neck"],
                "head": ["head"],
                "leftShoulder": ["left_shoulder", "l_shoulder"],
                "leftUpperArm": ["left_upper_arm", "l_upper_arm", "left_arm"],
                "leftLowerArm": ["left_lower_arm", "l_lower_arm", "left_forearm"],
                "leftHand": ["left_hand", "l_hand"],
                "rightShoulder": ["right_shoulder", "r_shoulder"],
                "rightUpperArm": ["right_upper_arm", "r_upper_arm", "right_arm"],
                "rightLowerArm": ["right_lower_arm", "r_lower_arm", "right_forearm"],
                "rightHand": ["right_hand", "r_hand"],
                "leftUpperLeg": ["left_upper_leg", "l_upper_leg", "left_thigh"],
                "leftLowerLeg": ["left_lower_leg", "l_lower_leg", "left_shin"],
                "leftFoot": ["left_foot", "l_foot"],
                "rightUpperLeg": ["right_upper_leg", "r_upper_leg", "right_thigh"],
                "rightLowerLeg": ["right_lower_leg", "r_lower_leg", "right_shin"],
                "rightFoot": ["right_foot", "r_foot"]
            }
            
            for i, node in enumerate(gltf.nodes):
                if hasattr(node, 'name') and node.name:
                    node_name_lower = node.name.lower()
                    
                    for vrm_bone, possible_names in bone_mapping.items():
                        if any(name in node_name_lower for name in possible_names):
                            humanoid_bones.append({
                                "bone": vrm_bone,
                                "node": i,
                                "useDefaultValues": True
                            })
                            break
        
        gltf.extensions["VRM"]["humanoid"]["humanBones"] = humanoid_bones
    
    def _setup_vrm_materials(self, gltf: GLTF2):
        """Set up VRM material properties"""
        material_properties = []
        
        if gltf.materials:
            for i, material in enumerate(gltf.materials):
                # Create basic VRM material property
                material_property = {
                    "name": material.name if hasattr(material, 'name') and material.name else f"Material_{i}",
                    "shader": "VRM/MToon",
                    "keywordMap": {},
                    "tagMap": {},
                    "floatProperties": {},
                    "vectorProperties": {},
                    "textureProperties": {}
                }
                
                # Copy basic material properties
                if hasattr(material, 'pbrMetallicRoughness') and material.pbrMetallicRoughness:
                    pbr = material.pbrMetallicRoughness
                    
                    # Base color
                    if hasattr(pbr, 'baseColorFactor') and pbr.baseColorFactor:
                        material_property["vectorProperties"]["_Color"] = pbr.baseColorFactor
                    
                    # Base color texture
                    if hasattr(pbr, 'baseColorTexture') and pbr.baseColorTexture:
                        material_property["textureProperties"]["_MainTex"] = pbr.baseColorTexture.index
                
                material_properties.append(material_property)
        
        gltf.extensions["VRM"]["materialProperties"] = material_properties