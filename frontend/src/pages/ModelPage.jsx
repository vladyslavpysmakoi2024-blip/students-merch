import React, { useState, Suspense, useEffect } from 'react'

import ModelGrid from '../components/ModelGrid';
import { api } from "../shared/api/instance";

import { Canvas } from "@react-three/fiber";
import { OrbitControls, Center, Environment } from "@react-three/drei";
import Model3dCharacter from "../components/Model3dCharacter";
import { div } from 'three/src/nodes/math/OperatorNode.js';

const fakeProducts = [
  {id: 0, type: "Футболки", name: "футболка 1", photo: null, price: 1200, texture: "/textures/tshirts/1.png"},
  {id: 1, type: "Футболки", name: "футболка 1", photo: null, price: 1200, texture: "/textures/tshirts/2.png"},
  {id: 2, type: "Шоппери", name: "шоппер 1", photo: null, price: 2000, texture: "/textures/bags/1.png"},
  {id: 3, type: "Шоппери", name: "шоппер 2", photo: null, price: 2000, texture: "/textures/bags/2.png"},
  {id: 4, type: "Шоппери", name: "шоппер 3", photo: null, price: 2000, texture: "/textures/bags/3.png"},
]

const ModelPage = () => {
     const [gender, setGender] = useState("male");
     const [products, setProducts] = useState(fakeProducts);
     const [isLoading, setIsLoading] = useState(false);
     const [activeModels, setActiveModels] = useState([{type: "Футболки"}]);

     const groupedProducts = products.reduce((acc, val) => {
        const key = val.type;
    
        if (!acc[key]) {
          acc[key] = [];
        }

        acc[key].push(val);

        return acc;
     }, {});

    //  useEffect(() => {
    //   const SetData = async () => {
    //     try {
    //       const response = await api.get("/clothing/simple-list");
    //       const data = response.data;
  
    //       setProducts(data);
    //     }
    //     catch(ex) {
    //       console.log(`Error fetching clothing: ${ex}`);
    //     }
    //     finally{
    //       setIsLoading(false);
    //     }
    //   }
  
      
    //   SetData();
    //  }, [])
  
     if (isLoading) {
       return (
         <div
           style={{
             padding: "50px",
             textAlign: "center",
             color: "#ffffff",
             fontSize: "18px",
           }}
         >
           Завантаження...
         </div>
       );
     }
 
  return (
    <>
        <div>
            <div className="model-card">

                <div id="model-container" >
                    <Canvas
                    camera={{ position: [0, 2, 6], fov: 45 }}>
                      <ambientLight intensity={0.7}/>
                      <directionalLight position={[5, 5, 5]} intensity={1.2}/>

                      <Suspense fallback={null}>
                        <Center>
                          <Model3dCharacter activeModels={activeModels} gender={gender} />
                        </Center>
                        <Environment preset="city" />
                      </Suspense>

                      <OrbitControls
                        makeDefault
                        enableZoom={false}
                        enablePan={false}
                        autoRotate
                        autoRotateSpeed={1.5} />
                    </Canvas>
                </div>

                <div className="gender-btns" >
                  <button onClick={() => setGender("female")} >Дівчинка</button>
                  <button onClick={() => setGender("male")} >Хлопчик</button>
                </div>

                {groupedProducts && Object.entries(groupedProducts).map(([ctg, arr]) => {
                return(
                  <ModelGrid key={ctg} ctg={ctg} items={arr} setActiveModels={setActiveModels} activeModels={activeModels} />
                )
                })}

            </div>
        </div>
    </>
  )
}

export default ModelPage