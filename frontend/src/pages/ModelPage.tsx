import React, { useState, Suspense } from "react";
import { Canvas } from "@react-three/fiber";
import { OrbitControls, Center } from "@react-three/drei";
import ModelGrid from "@components/ModelGrid";
import Model3dCharacter from "@components/Model3dCharacter";
import { ClothingItem } from "@shared/types/api";

const fakeProducts: ClothingItem[] = [
  {
    id: 0,
    type: "Футболки",
    name: "футболка 1",
    photo: "/textures/tshirts/1.png",
    photos: ["/textures/tshirts/1.png"],
    color: "#FFFFFF",
    price: 1200,
    texture: "/textures/tshirts/1.png",
  },
  {
    id: 1,
    type: "Футболки",
    name: "футболка 2",
    photo: "/textures/tshirts/2.png",
    photos: ["/textures/tshirts/2.png"],
    color: "#DCC9A6",
    price: 1200,
    texture: "/textures/tshirts/2.png",
  },
  {
    id: 2,
    type: "Шопери",
    name: "шопер 1",
    photo: "/textures/bags/1.png",
    photos: ["/textures/bags/1.png"],
    color: "#C2B280",
    price: 2000,
    texture: "/textures/bags/1.png",
  },
  {
    id: 3,
    type: "Шопери",
    name: "шопер 2",
    photo: "/textures/bags/2.png",
    photos: ["/textures/bags/2.png"],
    color: "#000000",
    price: 2000,
    texture: "/textures/bags/2.png",
  },
  {
    id: 4,
    type: "Шопери",
    name: "шопер 3",
    photo: "/textures/bags/3.png",
    photos: ["/textures/bags/3.png"],
    color: "#8FC3E8",
    price: 2000,
    texture: "/textures/bags/3.png",
  },
];

const isMobileViewport =
  typeof window !== "undefined" && window.innerWidth <= 768;

const ModelPage = () => {
  const [gender, setGender] = useState<"male" | "female">("male");
  const [products] = useState<ClothingItem[]>(fakeProducts);
  const [activeModels, setActiveModels] = useState<ClothingItem[]>([
    fakeProducts[0],
  ]);

  const groupedProducts = products.reduce<Record<string, ClothingItem[]>>(
    (acc, val) => {
      const key = val.type || "Інше";
      if (!acc[key]) {
        acc[key] = [];
      }
      acc[key].push(val);
      return acc;
    },
    {},
  );

  return (
    <div>
      <div className="model-card">
        <div id="model-container">
          <Canvas
            dpr={isMobileViewport ? [1, 1.25] : [1, 1.75]}
            gl={{
              powerPreference: "high-performance",
              antialias: !isMobileViewport,
            }}
            camera={{ position: [0, 2, 6], fov: 45 }}
          >
            <ambientLight intensity={1.1} />
            <hemisphereLight
              args={["#ffffff", "#d0dce5", 0.9]}
              position={[0, 10, 0]}
            />
            <directionalLight position={[5, 5, 5]} intensity={1.2} />
            <directionalLight position={[-4, 3, -4]} intensity={0.5} />

            <Suspense fallback={null}>
              <Center>
                <Model3dCharacter
                  activeModels={
                    activeModels as Array<
                      Partial<ClothingItem> & { type: string }
                    >
                  }
                  gender={gender}
                />
              </Center>
            </Suspense>

            <OrbitControls
              makeDefault
              enableZoom={false}
              enablePan={false}
              autoRotate
              autoRotateSpeed={1.5}
            />
          </Canvas>
        </div>

        <div className="gender-btns">
          <button onClick={() => setGender("female")}>Дівчинка</button>
          <button onClick={() => setGender("male")}>Хлопчик</button>
        </div>

        {Object.entries(groupedProducts).map(([ctg, arr]) => (
          <ModelGrid
            key={ctg}
            ctg={ctg}
            items={arr}
            setActiveModels={setActiveModels}
            activeModels={activeModels}
          />
        ))}
      </div>
    </div>
  );
};

export default ModelPage;
