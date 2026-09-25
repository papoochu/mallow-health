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
  TodayData,
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
  todayData: TodayData | null;

  loading: boolean;
  todayLoading: boolean;
  connecting: boolean;

  error: string | null;
  todayError: string | null;

  windowDays: ViewWindow;

  sourceMode: HealthSourceMode;
  deviceHealthAvailable: boolean;

  setWindowDays: (
    value: ViewWindow
  ) => void;

  refresh: () => Promise<void>;

  refreshToday: () => Promise<void>;

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

  const [todayData, setTodayData] = useState<TodayData | null>(
    null
  );

  const [loading, setLoading] = useState(
    true
  );

  const [todayLoading, setTodayLoading] = useState(
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

  const [todayError, setTodayError] = useState<string | null>(
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


  const loadTodayFromService = async (
    service: HealthDataService,
  ) => {
    try {
      setTodayLoading(
        true
      );

      setTodayError(
        null
      );

      if (
        service.getToday === undefined
      ) {
        setTodayData(
          null
        );

        setTodayError(
          service === deviceService
            ? (
              "Intraday device sampling is integration-ready but "
              + "still pending native iOS validation."
            )
            : "Intraday data is not available from this source."
        );

        return;
      }

      const nextToday = await service.getToday();

      setTodayData(
        nextToday
      );
    } catch (
      caught
    ) {
      const message = (
        caught instanceof Error
          ? caught.message
          : "Unable to load today's health data."
      );

      setTodayData(
        null
      );

      setTodayError(
        message
      );
    } finally {
      setTodayLoading(
        false
      );
    }
  };


  const refresh = async () => {
    await loadFromService(
      activeService
    );
  };


  const refreshToday = async () => {
    await loadTodayFromService(
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

      await loadTodayFromService(
        deviceService
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

    await Promise.all(
      [
        loadFromService(
          demoService
        ),
        loadTodayFromService(
          demoService
        ),
      ]
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


  useEffect(
    () => {
      void loadTodayFromService(
        activeService
      );
    },
    [
      sourceMode,
    ],
  );


  const value: HealthDataContextValue = {
    data,
    todayData,
    loading,
    todayLoading,
    connecting,
    error,
    todayError,
    windowDays,
    sourceMode,
    deviceHealthAvailable,
    setWindowDays,
    refresh,
    refreshToday,
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
