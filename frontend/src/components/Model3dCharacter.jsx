import React, { Suspense, useEffect, useRef } from 'react';
import * as THREE from "three";
import { useGLTF, useTexture } from "@react-three/drei";


const LoadClothing = ({ url, gender, objectName, textureUrl }) => {
    const clothing = useGLTF(url);
    const meshRef = useRef(null);

    useEffect(() => {
    
    const mesh = clothing.scene.getObjectByName(objectName);

    if (mesh && mesh.morphTargetDictionary && mesh.morphTargetInfluences) {
      meshRef.current = mesh;
      
      const keyIndex = mesh.morphTargetDictionary["Female"];
      
      if (keyIndex !== undefined) {
        mesh.morphTargetInfluences[keyIndex] = (gender === "male" ? 0 : 1);
      }
    }

    if (!textureUrl || !mesh.material) return;

    const loader = new THREE.TextureLoader();

    loader.load(
      textureUrl,
      (loadedTexture) => {
        loadedTexture.flipY = false;
        loadedTexture.colorSpace = THREE.SRGBColorSpace;
        loadedTexture.needsUpdate = true;

        const applyToMaterial = (mat) => {
          const newMat = mat.clone();
          newMat.color.set("#ffffff");
          newMat.map = loadedTexture;
          newMat.needsUpdate = true;
          return newMat;
        };

        if (Array.isArray(mesh.material)) {
          mesh.material = mesh.material.map(applyToMaterial);
        } else {
          mesh.material = applyToMaterial(mesh.material);
        }
      },
      undefined,
      (err) => console.error("Error loading texture:", err)
    );

  }, [clothing, gender, textureUrl]);

    return <primitive object={clothing.scene}/>;
}

const Model3dCharacter = ({ activeModels, gender }) => {

    const clothingUrls = {
        "Футболки": {
          name: "TShirt_Male",
          url: "/models/shared/tshirt.glb"
        }
    }
    
    const stickman = useGLTF(gender == "male" ? "/models/male/stickman.glb" : "/models/female/stickman.glb");

  return (
    <group>
        <primitive object={stickman.scene}/>
        <Suspense fallback={null} >
          {activeModels.map((model) => {
            const modelData = clothingUrls[model["type"]];
            
            return (
              <LoadClothing key={model["type"]} url={modelData["url"]} gender={gender} objectName={modelData["name"]} textureUrl={model["texture"]} />
            )
          })}
          <LoadClothing url={`/models/shared/sweatpants.glb`} gender={gender} objectName={"Sweatpants_Male"} />
        </Suspense>
    </group>
  )
}

useGLTF.preload("/models/male/stickman.glb");
useGLTF.preload("/models/female/stickman.glb");

export default Model3dCharacter