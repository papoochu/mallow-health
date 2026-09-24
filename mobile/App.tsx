import React, {
  useMemo,
  useState,
} from "react";

import {
  Platform,
  StatusBar as NativeStatusBar,
  StyleSheet,
  useColorScheme,
  View,
} from "react-native";

import {
  StatusBar,
} from "expo-status-bar";

import BottomNav, {
  TabKey,
} from "./src/components/BottomNav";

import {
  HealthDataProvider,
} from "./src/data/HealthDataContext";

import AskScreen from "./src/screens/AskScreen";
import HealthScreen from "./src/screens/HealthScreen";
import HomeScreen from "./src/screens/HomeScreen";
import SleepScreen from "./src/screens/SleepScreen";

import {
  createAppStyles,
  darkColors,
  lightColors,
} from "./src/theme/colors";


export default function App() {
  const systemScheme = useColorScheme();

  const [darkMode, setDarkMode] = useState(
    systemScheme === "dark"
  );

  const [activeTab, setActiveTab] = useState<TabKey>(
    "home"
  );

  const colors = (
    darkMode
      ? darkColors
      : lightColors
  );

  const styles = useMemo(
    () => createAppStyles(
      colors
    ),
    [
      colors,
    ],
  );

  const topInset = (
    Platform.OS === "android"
      ? NativeStatusBar.currentHeight ?? 0
      : 0
  );

  const renderScreen = () => {
    const sharedProps = {
      colors,
      darkMode,
      onToggleDarkMode: () => {
        setDarkMode(
          (
            current
          ) => !current
        );
      },
    };

    switch (
      activeTab
    ) {
      case "health":
        return (
          <HealthScreen
            {...sharedProps}
          />
        );

      case "sleep":
        return (
          <SleepScreen
            {...sharedProps}
          />
        );

      case "ask":
        return (
          <AskScreen
            {...sharedProps}
          />
        );

      case "home":
      default:
        return (
          <HomeScreen
            {...sharedProps}
            onOpenAsk={() => {
              setActiveTab(
                "ask"
              );
            }}
          />
        );
    }
  };

  return (
    <HealthDataProvider>
      <View
        style={[
          styles.root,
          {
            paddingTop: topInset,
          },
        ]}
      >
        <StatusBar
          style={
            darkMode
              ? "light"
              : "dark"
          }
        />

        <View
          style={styles.screenArea}
        >
          {
            renderScreen()
          }
        </View>

        <BottomNav
          activeTab={activeTab}
          onSelect={setActiveTab}
          colors={colors}
        />
      </View>
    </HealthDataProvider>
  );
}
