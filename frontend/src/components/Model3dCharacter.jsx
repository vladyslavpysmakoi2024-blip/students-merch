import React, { Suspense, useRef } from 'react';
import { useGLTF } from "@react-three/drei";
import { useFrame } from '@react-three/fiber';


const LoadClothing = ({ url }) => {
    const clothing = useGLTF(url);

    return <primitive object={clothing.scene}/>;
}

const Model3dCharacter = ({ clothingType }) => {
    const clothingUrls = {
        "Футболка": "/models/tshirt.glb"
    }

    const stickman = useGLTF("/models/stickman.glb");

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

useGLTF.preload("/models/stickman.glb");

export default Model3dCharacter