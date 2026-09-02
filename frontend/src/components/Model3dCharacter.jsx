import React, { Suspense } from 'react';
import { useGLTF } from "@react-three/drei";
import { useFrame } from '@react-three/fiber';


const LoadClothing = ({ url }) => {
    const clothing = useGLTF(url);

    return <primitive object={clothing.scene}/>;
}

const Model3dCharacter = ({ clothingType }) => {

    const clothingUrls = {
        "Футболка": "/models/shared/tshirt.glb"
    }
    
    const stickman = useGLTF("/models/male/stickman.glb");

  return (
    <group>
        <primitive object={stickman.scene}/>
        {clothingType && (
            <Suspense fallback={null} >
                <LoadClothing url={clothingUrls[clothingType]} />
            </Suspense>
        )}
    </group>
  )
}

useGLTF.preload("/models/male/stickman.glb");
useGLTF.preload("/models/female/stickman.glb");

export default Model3dCharacter