import React from "react";

import {
  StyleSheet,
  Text,
  View,
} from "react-native";

import {
  HealthMetricSnapshot,
} from "../models/health";

import {
  ThemeColors,
} from "../theme/colors";


type MetricCardProps = {
  metric: HealthMetricSnapshot;
  colors: ThemeColors;
  hero?: boolean;
};


export default function MetricCard({
  metric,
  colors,
  hero = false,
}: MetricCardProps) {
  const styles = createStyles(
    colors
  );

  const pillStyle = (
    metric.tone === "pink"
      ? styles.pinkPill
      : metric.tone === "warning"
        ? styles.warningPill
        : metric.tone === "neutral"
          ? styles.neutralPill
          : styles.goodPill
  );

  const pillTextStyle = (
    metric.tone === "pink"
      ? styles.pinkPillText
      : metric.tone === "warning"
        ? styles.warningPillText
        : metric.tone === "neutral"
          ? styles.neutralPillText
          : styles.goodPillText
  );

  return (
    <View
      style={
        hero
          ? styles.heroCard
          : styles.card
      }
    >
      <View
        style={styles.header}
      >
        <Text
          style={styles.title}
        >
          {metric.icon} {metric.title}
        </Text>

        {
          metric.source
            ? (
              <Text
                style={styles.source}
              >
                {metric.source}
              </Text>
            )
            : null
        }
      </View>

      <Text
        style={
          hero
            ? styles.heroValue
            : styles.value
        }
      >
        {metric.value}
      </Text>

      <Text
        style={styles.detail}
      >
        {metric.detail}
      </Text>

      <View
        style={pillStyle}
      >
        <Text
          style={pillTextStyle}
        >
          {metric.status}
        </Text>
      </View>
    </View>
  );
}


function createStyles(
  colors: ThemeColors,
) {
  return StyleSheet.create(
    {
      card: {
        backgroundColor: colors.surface,
        borderColor: colors.border,
        borderRadius: 20,
        borderWidth: 1,
        padding: 16,
      },

      heroCard: {
        backgroundColor: colors.surface,
        borderColor: colors.border,
        borderRadius: 24,
        borderWidth: 1,
        padding: 18,
      },

      header: {
        alignItems: "center",
        flexDirection: "row",
        justifyContent: "space-between",
      },

      title: {
        color: colors.textMuted,
        flex: 1,
        fontSize: 12,
        fontWeight: "700",
        paddingRight: 8,
      },

      source: {
        color: colors.textMuted,
        fontSize: 9,
      },

      value: {
        color: colors.text,
        fontSize: 25,
        fontWeight: "800",
        letterSpacing: -0.4,
        marginTop: 10,
      },

      heroValue: {
        color: colors.text,
        fontSize: 34,
        fontWeight: "800",
        letterSpacing: -1,
        marginTop: 15,
      },

      detail: {
        color: colors.textMuted,
        fontSize: 11,
        marginBottom: 10,
        marginTop: 4,
      },

      goodPill: {
        alignSelf: "flex-start",
        backgroundColor: colors.goodSoft,
        borderRadius: 999,
        paddingHorizontal: 10,
        paddingVertical: 6,
      },

      goodPillText: {
        color: colors.good,
        fontSize: 10,
        fontWeight: "700",
      },

      pinkPill: {
        alignSelf: "flex-start",
        backgroundColor: colors.pinkSoft,
        borderRadius: 999,
        paddingHorizontal: 10,
        paddingVertical: 6,
      },

      pinkPillText: {
        color: colors.pink,
        fontSize: 10,
        fontWeight: "700",
      },

      warningPill: {
        alignSelf: "flex-start",
        backgroundColor: colors.warningSoft,
        borderRadius: 999,
        paddingHorizontal: 10,
        paddingVertical: 6,
      },

      warningPillText: {
        color: colors.warning,
        fontSize: 10,
        fontWeight: "700",
      },

      neutralPill: {
        alignSelf: "flex-start",
        backgroundColor: colors.surfaceSoft,
        borderRadius: 999,
        paddingHorizontal: 10,
        paddingVertical: 6,
      },

      neutralPillText: {
        color: colors.textMuted,
        fontSize: 10,
        fontWeight: "700",
      },
    }
  );
}
