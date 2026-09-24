import React, {
  createContext,
  ReactNode,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";

import {
  DashboardData,
  HealthDataService,
  ViewWindow,
} from "../models/health";

import {
  DemoHealthService,
} from "../services/DemoHealthService";

import {
  DeviceHealthService,
} from "../services/DeviceHealthService";


export type HealthSourceMode =
  | "demo"
  | "device";


type HealthDataContextValue = {
  data: DashboardData | null;
  loading: boolean;
  connecting: boolean;
  error: string | null;

  windowDays: ViewWindow;

  sourceMode: HealthSourceMode;
  deviceHealthAvailable: boolean;

  setWindowDays: (
    value: ViewWindow
  ) => void;

  refresh: () => Promise<void>;

  ask: (
    question: string
  ) => Promise<string>;

  connectDeviceHealth: () => Promise<void>;

  useDemoData: () => Promise<void>;
};


const HealthDataContext = createContext<
  HealthDataContextValue | undefined
>(
  undefined
);


type HealthDataProviderProps = {
  children: ReactNode;
};


export function HealthDataProvider({
  children,
}: HealthDataProviderProps) {
  const demoService = useMemo(
    () => new DemoHealthService(),
    []
  );

  const deviceService = useMemo(
    () => new DeviceHealthService(),
    []
  );

  const [sourceMode, setSourceMode] = useState<HealthSourceMode>(
    "demo"
  );

  const [windowDays, setWindowDays] = useState<ViewWindow>(
    30
  );

  const [data, setData] = useState<DashboardData | null>(
    null
  );

  const [loading, setLoading] = useState(
    true
  );

  const [connecting, setConnecting] = useState(
    false
  );

  const [deviceHealthAvailable, setDeviceHealthAvailable] = useState(
    false
  );

  const [error, setError] = useState<string | null>(
    null
  );


  const activeService: HealthDataService = (
    sourceMode === "device"
      ? deviceService
      : demoService
  );


  const loadFromService = async (
    service: HealthDataService,
  ) => {
    try {
      setLoading(
        true
      );

      setError(
        null
      );

      const nextData = await service.getDashboard(
        windowDays
      );

      setData(
        nextData
      );
    } catch (
      caught
    ) {
      const message = (
        caught instanceof Error
          ? caught.message
          : "Unable to load health data."
      );

      setError(
        message
      );
    } finally {
      setLoading(
        false
      );
    }
  };


  const refresh = async () => {
    await loadFromService(
      activeService
    );
  };


  const ask = async (
    question: string
  ) => {
    return activeService.ask(
      question,
      windowDays,
    );
  };


  const connectDeviceHealth = async () => {
    try {
      setConnecting(
        true
      );

      setError(
        null
      );

      await deviceService.authorize();

      const nextData = await deviceService.getDashboard(
        windowDays
      );

      setSourceMode(
        "device"
      );

      setData(
        nextData
      );
    } catch (
      caught
    ) {
      const message = (
        caught instanceof Error
          ? caught.message
          : "Unable to connect device health data."
      );

      setError(
        message
      );

      throw caught;
    } finally {
      setConnecting(
        false
      );
    }
  };


  const useDemoData = async () => {
    setSourceMode(
      "demo"
    );

    await loadFromService(
      demoService
    );
  };


  useEffect(
    () => {
      void deviceService
        .isAvailable()
        .then(
          (
            available
          ) => {
            setDeviceHealthAvailable(
              available
            );
          }
        );
    },
    [
      deviceService,
    ],
  );


  useEffect(
    () => {
      void loadFromService(
        activeService
      );
    },
    [
      sourceMode,
      windowDays,
    ],
  );


  const value: HealthDataContextValue = {
    data,
    loading,
    connecting,
    error,
    windowDays,
    sourceMode,
    deviceHealthAvailable,
    setWindowDays,
    refresh,
    ask,
    connectDeviceHealth,
    useDemoData,
  };


  return (
    <HealthDataContext.Provider
      value={value}
    >
      {children}
    </HealthDataContext.Provider>
  );
}


export function useHealthData() {
  const context = useContext(
    HealthDataContext
  );

  if (
    context === undefined
  ) {
    throw new Error(
      "useHealthData must be used inside HealthDataProvider."
    );
  }

  return context;
}
