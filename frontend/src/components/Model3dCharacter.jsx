import React, { Suspense, useEffect, useRef, useMemo } from 'react';
import * as THREE from "three";
import { useGLTF } from "@react-three/drei";


const LoadClothing = ({ url, gender, objectName, textureUrl }) => {
  const gltf = useGLTF(url);

  const scene = useMemo(() => {
    if (!gltf?.scene) return null;
    return gltf.scene.clone(true);
  }, [gltf.scene]);

  const meshRef = useRef(null);

  useEffect(() => {
    if (!scene) return;

    let targetMesh = objectName ? scene.getObjectByName(objectName) : null;
    if (!targetMesh || !targetMesh.isMesh) {
      scene.traverse((child) => {
        if (child.isMesh && !targetMesh) {
          targetMesh = child;
        }
      });
    }

    if (targetMesh) {
      meshRef.current = targetMesh;
    }

    scene.traverse((child) => {
      if (child.isMesh && child.morphTargetDictionary && child.morphTargetInfluences) {
        const keyIndex = child.morphTargetDictionary["Female"];
        if (keyIndex !== undefined) {
          child.morphTargetInfluences[keyIndex] = gender === "male" ? 0 : 1;
        }
      }
    });

    if (!textureUrl) return;

    const loader = new THREE.TextureLoader();
    loader.load(
      textureUrl,
      (loadedTexture) => {
        loadedTexture.flipY = false;
        loadedTexture.colorSpace = THREE.SRGBColorSpace;
        loadedTexture.needsUpdate = true;

        const applyToMaterial = (mat) => {
          if (!mat) return mat;
          const newMat = mat.clone();
          newMat.color.set("#ffffff");
          newMat.map = loadedTexture;
          newMat.needsUpdate = true;
          return newMat;
        };

        scene.traverse((child) => {
          if (!child.isMesh || !child.material) return;

          if (child.name.toLowerCase().includes("strap")) return;

          const isTarget = objectName 
            ? child.name === objectName || child.name.includes(objectName)
            : true;

          if (isTarget) {
            if (Array.isArray(child.material)) {
              child.material = child.material.map(applyToMaterial);
            } else {
              child.material = applyToMaterial(child.material);
            }
          }
        });
      },
      undefined,
      (err) => console.error("Error loading texture:", err)
    );
  }, [scene, gender, textureUrl, objectName]);

  if (!scene) return null;

  return <primitive object={scene} />;
};

const Model3dCharacter = ({ activeModels, gender }) => {

    const clothingUrls = {
        "Футболки": {
          name: "TShirt_Male",
          url: "/models/shared/tshirt.glb"
        },
        "Шоппери": {
          "female": {
            name: "Bag",
            url: "/models/female/bag.glb"
          },
          "male": {
            name: "Bag",
            url: "/models/male/bag.glb"
          }
        }
    }
    
    const stickman = useGLTF(gender == "male" ? "/models/male/stickman.glb" : "/models/female/stickman.glb");

  return (
    <group>
        <primitive object={stickman.scene}/>
        <Suspense fallback={null} >
          {activeModels.map((model) => {
            let modelData = clothingUrls[model["type"]];
            const isNotShared = clothingUrls[model["type"]]["female"];

            if (isNotShared) {
              modelData = clothingUrls[model["type"]][gender];
            }
            
            return (
              <LoadClothing key={`${model["type"]}${gender}`} url={modelData["url"]} gender={gender} objectName={modelData["name"]} textureUrl={model["texture"]} />
            )
          })}
          <LoadClothing url={`/models/shared/sweatpants.glb`} gender={gender} objectName={"Sweatpants_Male"} />
        </Suspense>
    </group>
  )
}

useGLTF.preload("/models/male/stickman.glb");
useGLTF.preload("/models/female/stickman.glb");
useGLTF.preload("/models/male/bag.glb");
useGLTF.preload("/models/female/bag.glb");

export default Model3dCharacter