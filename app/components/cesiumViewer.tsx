"use client";

import { useEffect, useRef } from "react";
import {
  Ion,
  Viewer,
  createWorldTerrainAsync,
  Cartesian3,
  Color,
  SampledPositionProperty,
  JulianDate,
} from "cesium";
import "cesium/Build/Cesium/Widgets/widgets.css";

Ion.defaultAccessToken = process.env.NEXT_PUBLIC_CESIUM_ION_TOKEN || "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiI3YjIxYjgyYy01NWNiLTRiYTMtODM1OC05Yjc2NjkwNTBmY2IiLCJpZCI6MzQwMTY2LCJpYXQiOjE3NTc1MjEwNTd9._FD4RBe-8LYXN2BT5GNwNqFFzSyHnKsMaY8w_kSodEw";



export default function CesiumViewer() {
  const containerRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    (window as any).CESIUM_BASE_URL = "/cesium";

    const initCesium = async () => {
      const terrainProvider = await createWorldTerrainAsync();

      const viewer = new Viewer(containerRef.current!, {
        terrainProvider,
        animation: true,
        timeline: true,
      });

      // --- Timeline setup ---
      const start = JulianDate.now();
      const stop = JulianDate.addSeconds(start, 360, new JulianDate()); // 6 minutes

      viewer.clock.startTime = start.clone();
      viewer.clock.stopTime = stop.clone();
      viewer.clock.currentTime = start.clone();
      viewer.clock.clockRange = 2; // LOOP_STOP
      viewer.clock.multiplier = 10; // time speed

      // --- Sampled trajectory ---
      const position = new SampledPositionProperty();

      // Example nanosat path (long, lat, alt in meters)
      const nanosatPath = [
        [78.9629, 20.5937, 500000], // India
        [0.1276, 51.5072, 500000],  // London
        [-74.0060, 40.7128, 500000], // New York
        [139.6917, 35.6895, 500000], // Tokyo
      ];

      nanosatPath.forEach((coord, i) => {
        const time = JulianDate.addSeconds(start, i * 120, new JulianDate());
        const cartesian = Cartesian3.fromDegrees(coord[0], coord[1], coord[2]);
        position.addSample(time, cartesian);
      });

      // --- Add nanosat entity ---
      const satellite = viewer.entities.add({
        name: "Nanosatellite",
        position,
        point: { pixelSize: 10, color: Color.YELLOW },
        path: {
          resolution: 1,
          material: Color.CYAN,
          width: 2,
        },
      });

    viewer.scene.skyBox.show = false;
    viewer.scene.skyAtmosphere.show = false;
    viewer.scene.backgroundColor = Color.BLACK; // or transparent


      // Follow satellite with camera
      viewer.trackedEntity = satellite;

      return viewer
    };

    let viewerInstance: Viewer;
    initCesium().then(v => (viewerInstance = v));

    return () => {
      if (viewerInstance) viewerInstance.destroy();
    };
  }, []);

  return <div ref={containerRef} style={{ width: "100%", height: "100vh" }} />;
}

