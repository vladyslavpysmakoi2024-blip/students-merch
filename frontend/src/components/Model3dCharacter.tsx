import React, { Suspense, useEffect, useMemo } from "react";
import * as THREE from "three";
import { useGLTF } from "@react-three/drei";
import { ClothingItem } from "@shared/types/api";

const textureLoader = new THREE.TextureLoader();
const textureCache = new Map<string, THREE.Texture>();

function loadCachedTexture(
  url: string,
  onLoad: (texture: THREE.Texture) => void,
) {
  const cached = textureCache.get(url);
  if (cached) {
    onLoad(cached);
    return;
  }

  textureLoader.load(
    url,
    (loadedTexture) => {
      loadedTexture.flipY = false;
      loadedTexture.colorSpace = THREE.SRGBColorSpace;
      loadedTexture.generateMipmaps = false;
      loadedTexture.minFilter = THREE.LinearFilter;
      loadedTexture.needsUpdate = true;
      textureCache.set(url, loadedTexture);
      onLoad(loadedTexture);
    },
    undefined,
    (err) => console.error("Error loading texture:", err),
  );
}

interface LoadClothingProps {
  url: string;
  gender: "male" | "female";
  objectName?: string;
  textureUrl?: string | null;
}

const LoadClothing = ({
  url,
  gender,
  objectName,
  textureUrl,
}: LoadClothingProps) => {
  const gltf = useGLTF(url) as unknown as { scene?: THREE.Group };

  const scene = useMemo(() => {
    if (!gltf?.scene) return null;
    const cloned = gltf.scene.clone(true);
    cloned.traverse((child) => {
      const mesh = child as THREE.Mesh;
      if (!mesh.isMesh || !mesh.material) return;

      const cloneMat = (mat: THREE.Material) => {
        const m = mat.clone() as THREE.MeshStandardMaterial;
        m.normalMap = null;
        m.needsUpdate = true;
        return m;
      };

      mesh.material = Array.isArray(mesh.material)
        ? mesh.material.map(cloneMat)
        : cloneMat(mesh.material);
    });
    return cloned;
  }, [gltf?.scene]);

  useEffect(() => {
    if (!scene) return;

    scene.traverse((child) => {
      const mesh = child as THREE.Mesh;
      if (
        mesh.isMesh &&
        mesh.morphTargetDictionary &&
        mesh.morphTargetInfluences
      ) {
        const keyIndex = mesh.morphTargetDictionary["Female"];
        if (keyIndex !== undefined) {
          mesh.morphTargetInfluences[keyIndex] = gender === "male" ? 0 : 1;
        }
      }
    });
  }, [scene, gender]);

  useEffect(() => {
    if (!scene || !textureUrl) return;

    let cancelled = false;
    loadCachedTexture(textureUrl, (loadedTexture) => {
      if (cancelled) return;

      const updateMaterial = (mat: THREE.Material) => {
        const stdMat = mat as THREE.MeshStandardMaterial;
        if (stdMat.color) {
          stdMat.color.set("#ffffff");
        }
        stdMat.map = loadedTexture;
        stdMat.needsUpdate = true;
      };

      scene.traverse((child) => {
        const mesh = child as THREE.Mesh;
        if (!mesh.isMesh || !mesh.material) return;
        if (mesh.name.toLowerCase().includes("strap")) return;

        const isTarget = objectName
          ? mesh.name === objectName || mesh.name.includes(objectName)
          : true;

        if (isTarget) {
          if (Array.isArray(mesh.material)) {
            mesh.material.forEach(updateMaterial);
          } else {
            updateMaterial(mesh.material);
          }
        }
      });
    });

    return () => {
      cancelled = true;
    };
  }, [scene, textureUrl, objectName]);

  if (!scene) return null;

  return <primitive object={scene} />;
};

interface Model3dCharacterProps {
  activeModels: Array<Partial<ClothingItem> & { type: string }>;
  gender: "male" | "female";
}

const CLOTHING_URLS: Record<string, any> = {
  Футболки: {
    name: "TShirt_Male",
    url: "/models/shared/tshirt.glb",
  },
  Шопери: {
    female: {
      name: "Bag",
      url: "/models/female/bag.glb",
    },
    male: {
      name: "Bag",
      url: "/models/male/bag.glb",
    },
  },
};

const Model3dCharacter = ({ activeModels, gender }: Model3dCharacterProps) => {
  const stickman = useGLTF(
    gender === "male"
      ? "/models/male/stickman.glb"
      : "/models/female/stickman.glb",
  ) as unknown as { scene: THREE.Group };

  return (
    <group>
      <primitive object={stickman.scene} />
      <Suspense fallback={null}>
        {activeModels.map((model) => {
          const entry = CLOTHING_URLS[model.type];
          if (!entry) return null;
          const modelData = entry.female ? entry[gender] : entry;

          return (
            <LoadClothing
              key={
                entry.female
                  ? `${model.type}-${gender}`
                  : model.type
              }
              url={modelData.url}
              gender={gender}
              objectName={modelData.name}
              textureUrl={model.texture}
            />
          );
        })}
        <LoadClothing
          url="/models/shared/sweatpants.glb"
          gender={gender}
          objectName="Sweatpants_Male"
        />
      </Suspense>
    </group>
  );
};

useGLTF.preload("/models/male/stickman.glb");
useGLTF.preload("/models/female/stickman.glb");

export default Model3dCharacter;
