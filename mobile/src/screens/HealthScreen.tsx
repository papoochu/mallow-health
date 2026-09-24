import React from "react";

import {
  ScrollView,
  StyleSheet,
  Text,
  View,
} from "react-native";

import {
  ErrorState,
  LoadingState,
} from "../components/DataState";

import MetricCard from "../components/MetricCard";
import ScreenHeader from "../components/ScreenHeader";
import TimeWindowSelector from "../components/TimeWindowSelector";
import TrendCard from "../components/TrendCard";

import {
  useHealthData,
} from "../data/HealthDataContext";

import {
  ThemeColors,
} from "../theme/colors";


type HealthScreenProps = {
  colors: ThemeColors;
  darkMode: boolean;
  onToggleDarkMode: () => void;
};


export default function HealthScreen({
  colors,
  darkMode,
  onToggleDarkMode,
}: HealthScreenProps) {
  const {
    data,
    loading,
    error,
    windowDays,
    setWindowDays,
    refresh,
  } = useHealthData();

  const styles = createStyles(
    colors
  );


  if (
    loading
    && data === null
  ) {
    return (
      <LoadingState
        colors={colors}
      />
    );
  }


  if (
    error
    && data === null
  ) {
    return (
      <ErrorState
        colors={colors}
        message={error}
        onRetry={() => {
          void refresh();
        }}
      />
    );
  }


  if (
    data === null
  ) {
    return null;
  }


  return (
    <ScrollView
      style={styles.scroll}
      contentContainerStyle={styles.content}
      showsVerticalScrollIndicator={false}
    >
      <ScreenHeader
        colors={colors}
        darkMode={darkMode}
        onToggleDarkMode={onToggleDarkMode}
        title="Health ❤️"
        subtitle="heart, circulation, and metabolic data"
      />

      <TimeWindowSelector
        colors={colors}
        value={windowDays}
        onChange={setWindowDays}
      />

      <Text
        style={styles.sectionTitle}
      >
        Measurements
      </Text>

      <View
        style={styles.stack}
      >
        {
          data.healthMetrics.map(
            (
              metric
            ) => (
              <MetricCard
                key={metric.id}
                metric={metric}
                colors={colors}
              />
            )
          )
        }
      </View>

      <Text
        style={styles.sectionTitle}
      >
        HRV pattern
      </Text>

      <TrendCard
        colors={colors}
        title={data.hrvTrend.title}
        value={data.hrvTrend.value}
        caption={data.hrvTrend.caption}
        trendLabel={data.hrvTrend.trendLabel}
        data={data.hrvTrend.points}
      />

      <Text
        style={styles.note}
      >
        Source: {data.sourceLabel}. This service layer will later be replaced
        by HealthKit without changing this screen.
      </Text>
    </ScrollView>
  );
}


function createStyles(
  colors: ThemeColors,
) {
  return StyleSheet.create(
    {
      scroll: {
        flex: 1,
      },

      content: {
        paddingBottom: 118,
        paddingHorizontal: 18,
        paddingTop: 18,
      },

      sectionTitle: {
        color: colors.heading,
        fontSize: 18,
        fontWeight: "800",
        marginBottom: 10,
        marginTop: 4,
      },

      stack: {
        gap: 10,
        marginBottom: 24,
      },

      note: {
        color: colors.textMuted,
        fontSize: 10,
        lineHeight: 16,
        marginTop: 18,
        textAlign: "center",
      },
    }
  );
}
