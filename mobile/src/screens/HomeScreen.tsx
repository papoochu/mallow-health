import React from "react";

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

import DataSourceCard from "../components/DataSourceCard";
import InsightCard from "../components/InsightCard";
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


type HomeScreenProps = {
  colors: ThemeColors;
  darkMode: boolean;
  onToggleDarkMode: () => void;
  onOpenAsk: () => void;
};


export default function HomeScreen({
  colors,
  darkMode,
  onToggleDarkMode,
  onOpenAsk,
}: HomeScreenProps) {
  const {
    data,
    loading,
    error,
    windowDays,
    setWindowDays,
    refresh,
    sourceMode,
    deviceHealthAvailable,
    connecting,
    connectDeviceHealth,
    useDemoData,
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
      />

      <DataSourceCard
        colors={colors}
        sourceMode={sourceMode}
        deviceHealthAvailable={deviceHealthAvailable}
        connecting={connecting}
        onConnect={() => {
          void connectDeviceHealth();
        }}
        onUseDemo={() => {
          void useDemoData();
        }}
      />

      <View
        style={styles.sourceRow}
      >
        <Text
          style={styles.sourceText}
        >
          {data.sourceLabel}
        </Text>

        <Text
          style={styles.sourceText}
        >
          {data.lastUpdatedLabel}
        </Text>
      </View>

      <View
        style={styles.welcomeCard}
      >
        <Text
          style={styles.welcomeEyebrow}
        >
          Good morning ☀️
        </Text>

        <Text
          style={styles.welcomeTitle}
        >
          Here’s how you’ve been doing.
        </Text>

        <Text
          style={styles.welcomeBody}
        >
          Mallow compares recent measurements with your own history instead
          of treating every value like a universal threshold.
        </Text>
      </View>

      <TimeWindowSelector
        colors={colors}
        value={windowDays}
        onChange={setWindowDays}
      />

      <View
        style={styles.sectionHeader}
      >
        <Text
          style={styles.sectionTitle}
        >
          Overview
        </Text>

        <Text
          style={styles.sectionHint}
        >
          {windowDays}-day context
        </Text>
      </View>

      {
        data.overviewMetrics.length > 0
          ? (
            <>
              <MetricCard
                metric={
                  data.overviewMetrics[
                    0
                  ]
                }
                colors={colors}
                hero
              />

              <View
                style={styles.metricStack}
              >
                {
                  data.overviewMetrics.slice(
                    1
                  ).map(
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
            </>
          )
          : (
            <Text
              style={styles.emptyText}
            >
              No overview measurements are available yet.
            </Text>
          )
      }

      <View
        style={styles.sectionHeader}
      >
        <Text
          style={styles.sectionTitle}
        >
          Recent pattern
        </Text>
      </View>

      <TrendCard
        colors={colors}
        title={data.hrvTrend.title}
        value={data.hrvTrend.value}
        caption={data.hrvTrend.caption}
        trendLabel={data.hrvTrend.trendLabel}
        data={data.hrvTrend.points}
      />

      <View
        style={styles.sectionHeader}
      >
        <Text
          style={styles.sectionTitle}
        >
          Mallow noticed 🌱
        </Text>
      </View>

      <InsightCard
        colors={colors}
        title={data.overviewInsight.title}
        body={data.overviewInsight.body}
        support={data.overviewInsight.support}
      />

      <Pressable
        onPress={onOpenAsk}
        style={styles.askCard}
      >
        <View
          style={styles.askIconWrap}
        >
          <Text
            style={styles.askIcon}
          >
            💬
          </Text>
        </View>

        <View
          style={styles.askCopy}
        >
          <Text
            style={styles.askTitle}
          >
            Ask Mallow
          </Text>

          <Text
            style={styles.askText}
          >
            “How has my sleep changed this month?”
          </Text>
        </View>

        <Text
          style={styles.chevron}
        >
          ›
        </Text>
      </Pressable>

      <Text
        style={styles.disclaimer}
      >
        Mallow summarizes personal health data and statistical patterns.
        It is not intended for diagnosis, treatment, or emergency
        decision-making.
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

      sourceRow: {
        flexDirection: "row",
        justifyContent: "space-between",
        marginBottom: 12,
      },

      sourceText: {
        color: colors.textMuted,
        fontSize: 10,
      },

      welcomeCard: {
        backgroundColor: colors.surfaceSoft,
        borderColor: colors.border,
        borderRadius: 24,
        borderWidth: 1,
        marginBottom: 16,
        padding: 20,
      },

      welcomeEyebrow: {
        color: colors.heading,
        fontSize: 13,
        fontWeight: "700",
        marginBottom: 9,
      },

      welcomeTitle: {
        color: colors.text,
        fontSize: 22,
        fontWeight: "800",
        letterSpacing: -0.4,
        lineHeight: 28,
      },

      welcomeBody: {
        color: colors.textMuted,
        fontSize: 13,
        lineHeight: 20,
        marginTop: 10,
      },

      sectionHeader: {
        alignItems: "center",
        flexDirection: "row",
        justifyContent: "space-between",
        marginBottom: 10,
        marginTop: 22,
      },

      sectionTitle: {
        color: colors.heading,
        fontSize: 18,
        fontWeight: "800",
      },

      sectionHint: {
        color: colors.textMuted,
        fontSize: 11,
      },

      metricStack: {
        gap: 10,
        marginTop: 10,
      },

      emptyText: {
        color: colors.textMuted,
        fontSize: 12,
        lineHeight: 18,
        paddingVertical: 18,
        textAlign: "center",
      },

      askCard: {
        alignItems: "center",
        backgroundColor: colors.surface,
        borderColor: colors.border,
        borderRadius: 22,
        borderWidth: 1,
        flexDirection: "row",
        marginBottom: 20,
        marginTop: 14,
        padding: 15,
      },

      askIconWrap: {
        alignItems: "center",
        backgroundColor: colors.accentSoft,
        borderRadius: 16,
        height: 44,
        justifyContent: "center",
        marginRight: 12,
        width: 44,
      },

      askIcon: {
        fontSize: 18,
      },

      askCopy: {
        flex: 1,
      },

      askTitle: {
        color: colors.text,
        fontSize: 14,
        fontWeight: "800",
      },

      askText: {
        color: colors.textMuted,
        fontSize: 11,
        marginTop: 3,
      },

      chevron: {
        color: colors.textMuted,
        fontSize: 28,
        marginLeft: 8,
      },

      disclaimer: {
        color: colors.textMuted,
        fontSize: 10,
        lineHeight: 16,
        paddingHorizontal: 6,
        textAlign: "center",
      },
    }
  );
}
