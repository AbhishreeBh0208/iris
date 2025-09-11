"use client";

import { useState } from "react";

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

interface MissionParameters {
  target_object: string;
  intercept_date: string;
  swarm_size: number;
  role_split: string;
  propulsion_type: string;
}

interface Props {
  isOpen: boolean;
  onClose: () => void;
  missionResult: MissionResult | null;
}

export default function MissionSimulationModal({ isOpen, onClose, missionResult }: Props) {
  if (!isOpen || !missionResult) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-75">
      <div className="mx-4 w-full max-w-2xl max-h-[90vh] overflow-y-auto rounded-2xl bg-gray-900 p-6 text-white shadow-2xl">
        <div className="p-6 text-white">
          <div className="grid grid-cols-2 gap-4 mb-6">
            <div className="bg-gray-800 p-4 rounded-lg">
              <div className="text-gray-400 text-sm">Delta-V Required</div>
              <div className="text-2xl font-bold text-blue-400">
                {missionResult.delta_v_required_km_s?.toFixed(3) || '0.000'} km/s
              </div>
            </div>
            <div className="bg-gray-800 p-4 rounded-lg">
              <div className="text-gray-400 text-sm">Time of Flight</div>
              <div className="text-2xl font-bold text-purple-400">
                {missionResult.flight_time_days?.toFixed(1) || '0.0'} days
              </div>
            </div>
            <div className="bg-gray-800 p-4 rounded-lg">
              <div className="text-gray-400 text-sm">Fuel Consumed</div>
              <div className="text-2xl font-bold text-orange-400">
                {missionResult.fuel_consumed_percent?.toFixed(1) || '0.0'}%
              </div>
            </div>
            <div className="bg-gray-800 p-4 rounded-lg">
              <div className="text-gray-400 text-sm">Success Probability</div>
              <div className="text-2xl font-bold text-green-400">
                {((missionResult.success_probability || 0) * 100).toFixed(1)}%
              </div>
            </div>
          </div>

          {missionResult.data_captured && missionResult.data_captured.length > 0 && (
            <div className="bg-gray-800 p-4 rounded-lg mb-6">
              <h3 className="text-lg font-bold mb-3 text-green-400">Data Captured</h3>
              <div className="space-y-2">
                {missionResult.data_captured.map((item, index) => (
                  <div key={index} className="flex items-center space-x-2 text-gray-300">
                    <span className="text-green-400">•</span>
                    <span>{item}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="bg-gray-800 p-4 rounded-lg mb-6">
            <h3 className="text-lg font-bold mb-3 text-purple-400">Transfer Trajectory</h3>
            <div className="text-sm text-gray-300 mb-2">
              Computed using real orbital mechanics and trajectory data
            </div>
            <div className="bg-gray-900 p-3 rounded text-xs font-mono">
              <div className="text-gray-400">
                Data sources: {missionResult.data_sources.join(', ')}
              </div>
              <div className="text-gray-400">
                Target: {missionResult.target_object} → Intercept: {missionResult.intercept_date}
              </div>
              {missionResult.miss_distance_km && (
                <div className="text-gray-400 mt-2">
                  Miss distance: {(missionResult.miss_distance_km / 1000).toFixed(0)} km
                </div>
              )}
              {missionResult.relative_velocity_km_per_s && (
                <div className="text-gray-400">
                  Relative velocity: {missionResult.relative_velocity_km_per_s.toFixed(2)} km/s
                </div>
              )}
            </div>
          </div>

          <div className="bg-gray-800 p-4 rounded-lg mb-6">
            <h3 className="text-lg font-bold mb-3 text-blue-400">Mission Status</h3>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span className="text-gray-400">Status:</span>
                <span className={`ml-2 ${missionResult.success ? 'text-green-400' : 'text-red-400'}`}>
                  {missionResult.success ? 'SUCCESS' : 'FAILED'}
                </span>
              </div>
              <div>
                <span className="text-gray-400">Feasible:</span>
                <span className={`ml-2 ${missionResult.feasible ? 'text-green-400' : 'text-yellow-400'}`}>
                  {missionResult.feasible ? 'YES' : 'CHALLENGING'}
                </span>
              </div>
              <div>
                <span className="text-gray-400">Target:</span>
                <span className="ml-2 text-white">{missionResult.target_object}</span>
              </div>
              <div>
                <span className="text-gray-400">Intercept Time:</span>
                <span className="ml-2 text-white">
                  {missionResult.intercept_time ? new Date(missionResult.intercept_time).toLocaleDateString() : 'N/A'}
                </span>
              </div>
            </div>
          </div>

          {missionResult.error && (
            <div className="bg-red-900 border border-red-600 p-4 rounded-lg mb-6">
              <h3 className="text-lg font-bold mb-2 text-red-400">Error</h3>
              <div className="text-red-300 text-sm">{missionResult.error}</div>
            </div>
          )}

          <div className="flex space-x-4">
            <button 
              onClick={onClose}
              className="flex-1 bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-6 rounded-lg transition-colors"
            >
              🚀 NEW MISSION
            </button>
            <button 
              onClick={onClose}
              className="flex-1 bg-gray-600 hover:bg-gray-700 text-white font-bold py-3 px-6 rounded-lg transition-colors"
            >
              CLOSE
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
