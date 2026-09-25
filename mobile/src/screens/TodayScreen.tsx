import React, {
  useEffect,
  useMemo,
  useState,
} from "react";

import {
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from "react-native";

import {
  ErrorState,
  LoadingState,
} from "../components/DataState";

import IntradayChart from "../components/IntradayChart";
import ScreenHeader from "../components/ScreenHeader";
import TodayMetricCard from "../components/TodayMetricCard";

import {
  useHealthData,
} from "../data/HealthDataContext";

import {
  IntradayMetricKey,
} from "../models/health";

import {
  ThemeColors,
} from "../theme/colors";


type TodayScreenProps = {
  colors: ThemeColors;
  darkMode: boolean;
  onToggleDarkMode: () => void;
};


export default function TodayScreen({
  colors,
  darkMode,
  onToggleDarkMode,
}: TodayScreenProps) {
  const {
    todayData,
    todayLoading,
    todayError,
    refreshToday,
    sourceMode,
  } = useHealthData();

  const [selectedMetric, setSelectedMetric] = useState<IntradayMetricKey>(
    "heart_rate"
  );

  const styles = createStyles(
    colors
  );


  useEffect(
    () => {
      if (
        todayData === null
        || todayData.metrics.length === 0
      ) {
        return;
      }

      const selectedExists = todayData.metrics.some(
        (
          metric
        ) => metric.id === selectedMetric
      );

      if (
        !selectedExists
      ) {
        setSelectedMetric(
          todayData.metrics[
            0
          ].id
        );
      }
    },
    [
      selectedMetric,
      todayData,
    ],
  );


  const activeMetric = useMemo(
    () => (
      todayData?.metrics.find(
        (
          metric
        ) => metric.id === selectedMetric
      )
      ?? todayData?.metrics[
        0
      ]
      ?? null
    ),
    [
      selectedMetric,
      todayData,
    ],
  );


  if (
    todayLoading
    && todayData === null
  ) {
    return (
      <LoadingState
        colors={colors}
      />
    );
  }


  if (
    todayError
    && todayData === null
  ) {
    return (
      <View
        style={styles.stateRoot}
      >
        <ErrorState
          colors={colors}
          message={todayError}
          onRetry={() => {
            void refreshToday();
          }}
        />

        {
          sourceMode === "device"
            ? (
              <Text
                style={styles.nativeNote}
              >
                The daily HealthKit integration remains separate and
                integration-ready; intraday device validation is intentionally
                not being claimed without a signed native iOS build.
              </Text>
            )
            : null
        }
      </View>
    );
  }


  if (
    todayData === null
    || activeMetric === null
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
        title="Today ☀️"
        subtitle="intraday measurements and patterns"
      />

      <View
        style={styles.summaryCard}
      >
        <View>
          <Text
            style={styles.date}
          >
            {todayData.dateLabel}
          </Text>

          <Text
            style={styles.source}
          >
            {todayData.sourceLabel}
          </Text>
        </View>

        <View
          style={styles.summaryRight}
        >
          <Text
            style={styles.updated}
          >
            {todayData.lastUpdatedLabel}
          </Text>

          <Pressable
            onPress={() => {
              void refreshToday();
            }}
            style={styles.refreshButton}
          >
            <Text
              style={styles.refreshText}
            >
              Refresh
            </Text>
          </Pressable>
        </View>
      </View>

      <Text
        style={styles.intro}
      >
        Today uses measurements sampled throughout the day. These values can
        naturally move with activity, meals, posture, sleep, and timing, so
        Mallow summarizes the pattern rather than labeling each point as
        medically good or bad.
      </Text>

      <Text
        style={styles.sectionTitle}
      >
        Choose a measurement
      </Text>

      <ScrollView
        horizontal
        contentContainerStyle={styles.metricSelector}
        showsHorizontalScrollIndicator={false}
      >
        {
          todayData.metrics.map(
            (
              metric
            ) => {
              const active = (
                metric.id === activeMetric.id
              );

              return (
                <Pressable
                  key={metric.id}
                  onPress={() => {
                    setSelectedMetric(
                      metric.id
                    );
                  }}
                  style={[
                    styles.metricChip,
                    active
                      ? styles.metricChipActive
                      : null,
                  ]}
                >
                  <Text
                    style={styles.metricChipIcon}
                  >
                    {metric.icon}
                  </Text>

                  <Text
                    style={[
                      styles.metricChipText,
                      active
                        ? styles.metricChipTextActive
                        : null,
                    ]}
                  >
                    {metric.title}
                  </Text>
                </Pressable>
              );
            }
          )
        }
      </ScrollView>

      <TodayMetricCard
        colors={colors}
        metric={activeMetric}
      />

      <IntradayChart
        colors={colors}
        metric={activeMetric}
      />

      <View
        style={styles.sectionRow}
      >
        <Text
          style={styles.sectionTitle}
        >
          Today at a glance
        </Text>

        <Text
          style={styles.sampleCount}
        >
          {todayData.totalSampleCount} timeline samples
        </Text>
      </View>

      <View
        style={styles.metricStack}
      >
        {
          todayData.metrics
            .filter(
              (
                metric
              ) => metric.id !== activeMetric.id
            )
            .map(
              (
                metric
              ) => (
                <TodayMetricCard
                  key={metric.id}
                  colors={colors}
                  metric={metric}
                  compact
                />
              )
            )
        }
      </View>

      <View
        style={styles.infoCard}
      >
        <Text
          style={styles.infoTitle}
        >
          Why Today is separate from your baseline
        </Text>

        <Text
          style={styles.infoBody}
        >
          A daytime heart-rate sample and a resting heart-rate measurement are
          not interchangeable. Mallow keeps intraday samples in their own
          timeline and uses daily measurements for longer-term personal
          baselines, trends, and relationships.
        </Text>
      </View>

      <Text
        style={styles.disclaimer}
      >
        Today is a descriptive personal-data view, not continuous clinical
        monitoring or an emergency alert system.
      </Text>
    </ScrollView>
  );
}


function createStyles(
  colors: ThemeColors,
) {
  return StyleSheet.create(
    {
      stateRoot: {
        flex: 1,
      },

      scroll: {
        flex: 1,
      },

      content: {
        paddingBottom: 118,
        paddingHorizontal: 18,
        paddingTop: 18,
      },

      summaryCard: {
        alignItems: "flex-start",
        backgroundColor: colors.surfaceSoft,
        borderColor: colors.border,
        borderRadius: 20,
        borderWidth: 1,
        flexDirection: "row",
        justifyContent: "space-between",
        padding: 15,
      },

      date: {
        color: colors.text,
        fontSize: 13,
        fontWeight: "800",
      },

      source: {
        color: colors.textMuted,
        fontSize: 9,
        marginTop: 4,
      },

      summaryRight: {
        alignItems: "flex-end",
        maxWidth: "45%",
      },

      updated: {
        color: colors.textMuted,
        fontSize: 9,
        textAlign: "right",
      },

      refreshButton: {
        backgroundColor: colors.accentSoft,
        borderRadius: 12,
        marginTop: 7,
        paddingHorizontal: 10,
        paddingVertical: 6,
      },

      refreshText: {
        color: colors.accent,
        fontSize: 9,
        fontWeight: "800",
      },

      intro: {
        color: colors.textMuted,
        fontSize: 11,
        lineHeight: 18,
        marginTop: 14,
      },

      sectionTitle: {
        color: colors.heading,
        fontSize: 16,
        fontWeight: "800",
        marginBottom: 10,
        marginTop: 22,
      },

      metricSelector: {
        gap: 8,
        paddingBottom: 13,
      },

      metricChip: {
        alignItems: "center",
        backgroundColor: colors.surface,
        borderColor: colors.border,
        borderRadius: 16,
        borderWidth: 1,
        flexDirection: "row",
        paddingHorizontal: 11,
        paddingVertical: 9,
      },

      metricChipActive: {
        backgroundColor: colors.accentSoft,
        borderColor: colors.accent,
      },

      metricChipIcon: {
        fontSize: 13,
        marginRight: 6,
      },

      metricChipText: {
        color: colors.textMuted,
        fontSize: 10,
        fontWeight: "700",
      },

      metricChipTextActive: {
        color: colors.accent,
      },

      sectionRow: {
        alignItems: "flex-end",
        flexDirection: "row",
        justifyContent: "space-between",
        marginTop: 4,
      },

      sampleCount: {
        color: colors.textMuted,
        fontSize: 8,
        marginBottom: 11,
      },

      metricStack: {
        gap: 9,
      },

      infoCard: {
        backgroundColor: colors.pinkSoft,
        borderColor: colors.border,
        borderRadius: 20,
        borderWidth: 1,
        marginTop: 18,
        padding: 16,
      },

      infoTitle: {
        color: colors.text,
        fontSize: 12,
        fontWeight: "800",
      },

      infoBody: {
        color: colors.textMuted,
        fontSize: 10,
        lineHeight: 16,
        marginTop: 7,
      },

      disclaimer: {
        color: colors.textMuted,
        fontSize: 9,
        lineHeight: 15,
        marginTop: 18,
        paddingHorizontal: 8,
        textAlign: "center",
      },

      nativeNote: {
        color: colors.textMuted,
        fontSize: 10,
        lineHeight: 16,
        paddingBottom: 28,
        paddingHorizontal: 28,
        textAlign: "center",
      },
    }
  );
}
