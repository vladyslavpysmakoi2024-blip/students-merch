import React, { Suspense, useEffect, useRef } from 'react';
import { useGLTF } from "@react-three/drei";
import { useFrame } from '@react-three/fiber';


const LoadClothing = ({ url, gender }) => {
    const clothing = useGLTF(url);
    const meshRef = useRef(null);

    useEffect(() => {
    
    const mesh = clothing.scene.getObjectByName("TShirt_Male");

    if (mesh && mesh.morphTargetDictionary && mesh.morphTargetInfluences) {
      meshRef.current = mesh;
      
      const keyIndex = mesh.morphTargetDictionary["TShirt_Female"];
      
      if (keyIndex !== undefined) {
        mesh.morphTargetInfluences[keyIndex] = (gender === "male" ? 0 : 1);
      }
    }

  }, [clothing, gender]);

    return <primitive object={clothing.scene}/>;
}

const Model3dCharacter = ({ clothingType, gender }) => {

    const clothingUrls = {
        "Футболка": "/models/shared/tshirt.glb"
    }
    
    const stickman = useGLTF(gender == "male" ? "/models/male/stickman.glb" : "/models/female/stickman.glb");

  return (
    <group>
        <primitive object={stickman.scene}/>
        {clothingType && (
            <Suspense fallback={null} >
                <LoadClothing url={clothingUrls[clothingType]} gender={gender} />
            </Suspense>
        )}
    </group>
  )
}

useGLTF.preload("/models/male/stickman.glb");
useGLTF.preload("/models/female/stickman.glb");

export default Model3dCharacter