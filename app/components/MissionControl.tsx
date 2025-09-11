"use client";

import { useState } from "react";
import MissionSimulationModal from "./MissionSimulationModal";

interface MissionResult {
  success: boolean;
  target_object: string;
  intercept_date: string;
  data_sources: string[];
  intercept_time?: string;
  target_position?: { x: number; y: number; z: number };
  interceptor_position?: { x: number; y: number; z: number };
  miss_distance_au?: number;
  miss_distance_km?: number;
  relative_velocity_km_per_s?: number;
  feasible?: boolean;
  interceptor_trajectory?: any[];
  error?: string;
  // REAL MISSION PARAMETERS - NO DEMO DATA
  delta_v_required_km_s?: number;
  flight_time_days?: number;
  fuel_consumed_percent?: number;
  success_probability?: number;
  data_captured?: string[];
}

export default function MissionControl() {
  const [isSimulating, setIsSimulating] = useState(false);
  const [missionResult, setMissionResult] = useState<MissionResult | null>(null);
  const [showModal, setShowModal] = useState(false);
  const [targetObject, setTargetObject] = useState("99942"); // Apophis
  const [interceptDate, setInterceptDate] = useState("2029-04-13T21:46:00Z");
  const [swarmSize, setSwarmSize] = useState(5);
  const [propulsionType, setPropulsionType] = useState("ion");

  const simulateMission = async () => {
    setIsSimulating(true);
    
    try {
      const missionParams = {
        target_object: targetObject,
        intercept_date: interceptDate,
        swarm_size: swarmSize,
        role_split: "balanced",
        propulsion_type: propulsionType
      };

      console.log("Simulating mission with params:", missionParams);

      // Call the Next.js API route which will call the backend
      const response = await fetch("/api/simulate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(missionParams),
      });

      if (!response.ok) {
        throw new Error(`Backend responded with status: ${response.status}`);
      }

      const result = await response.json();
      console.log("Mission simulation result:", result);

      setMissionResult(result);
      setShowModal(true);
    } catch (error) {
      console.error("Mission simulation failed:", error);
      
      // Show error in modal
      setMissionResult({
        success: false,
        target_object: targetObject,
        intercept_date: interceptDate,
        data_sources: [],
        error: `Mission simulation failed: ${error instanceof Error ? error.message : 'Unknown error'}`
      });
      setShowModal(true);
    } finally {
      setIsSimulating(false);
    }
  };

  return (
    <div className="absolute top-4 right-4 z-50">
      <div className="bg-gray-900 border border-gray-600 rounded-lg p-4 w-80">
        <h2 className="text-white text-lg font-bold mb-4">🚀 Mission Control</h2>
        
        <div className="space-y-3">
          <div>
            <label className="block text-gray-300 text-sm mb-1">Target Object</label>
            <input
              type="text"
              value={targetObject}
              onChange={(e) => setTargetObject(e.target.value)}
              className="w-full bg-gray-800 border border-gray-600 rounded px-3 py-2 text-white text-sm"
              placeholder="99942 (Apophis)"
            />
          </div>
          
          <div>
            <label className="block text-gray-300 text-sm mb-1">Intercept Date</label>
            <input
              type="datetime-local"
              value={interceptDate.slice(0, -1)} // Remove Z for input
              onChange={(e) => setInterceptDate(e.target.value + "Z")}
              className="w-full bg-gray-800 border border-gray-600 rounded px-3 py-2 text-white text-sm"
            />
          </div>
          
          <div>
            <label className="block text-gray-300 text-sm mb-1">Swarm Size</label>
            <input
              type="number"
              value={swarmSize}
              onChange={(e) => setSwarmSize(parseInt(e.target.value))}
              min="1"
              max="20"
              className="w-full bg-gray-800 border border-gray-600 rounded px-3 py-2 text-white text-sm"
            />
          </div>
          
          <div>
            <label className="block text-gray-300 text-sm mb-1">Propulsion</label>
            <select
              value={propulsionType}
              onChange={(e) => setPropulsionType(e.target.value)}
              className="w-full bg-gray-800 border border-gray-600 rounded px-3 py-2 text-white text-sm"
            >
              <option value="ion">Ion Drive</option>
              <option value="chemical">Chemical</option>
              <option value="nuclear">Nuclear</option>
            </select>
          </div>
        </div>
        
        <button
          onClick={simulateMission}
          disabled={isSimulating}
          className={`w-full mt-4 py-2 px-4 rounded font-bold text-white transition-colors ${
            isSimulating
              ? "bg-gray-600 cursor-not-allowed"
              : "bg-blue-600 hover:bg-blue-700"
          }`}
        >
          {isSimulating ? "🔄 Simulating..." : "🎯 SIMULATE MISSION"}
        </button>
        
        <div className="mt-3 text-xs text-gray-400">
          Real data from NASA JPL Horizons, MPC, and orbital mechanics calculations
        </div>
      </div>

      <MissionSimulationModal
        isOpen={showModal}
        onClose={() => {
          setShowModal(false);
          setMissionResult(null);
        }}
        missionResult={missionResult}
      />
    </div>
  );
}
