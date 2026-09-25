import React from "react";

import {
  StyleSheet,
  Text,
  View,
} from "react-native";

import {
  TodayMetricSummary,
} from "../models/health";

import {
  ThemeColors,
} from "../theme/colors";


type TodayMetricCardProps = {
  colors: ThemeColors;
  metric: TodayMetricSummary;
  compact?: boolean;
};


function formatValue(
  metric: TodayMetricSummary,
  value: number | null,
): string {
  if (
    value === null
  ) {
    return "No data";
  }

  const number = (
    metric.id === "wrist_temperature"
      ? (
        value >= 0
          ? `+${value.toFixed(metric.decimals)}`
          : value.toFixed(
              metric.decimals
            )
      )
      : value.toFixed(
          metric.decimals
        )
  );

  return `${number} ${metric.unit}`;
}


export default function TodayMetricCard({
  colors,
  metric,
  compact = false,
}: TodayMetricCardProps) {
  const styles = createStyles(
    colors
  );

  if (
    compact
  ) {
    return (
      <View
        style={styles.compactCard}
      >
        <View
          style={styles.compactHeader}
        >
          <Text
            style={styles.compactTitle}
          >
            {metric.icon} {metric.title}
          </Text>

          <Text
            style={styles.source}
          >
            {metric.source}
          </Text>
        </View>

        <Text
          style={styles.compactValue}
        >
          {formatValue(
            metric,
            metric.latest,
          )}
        </Text>

        <Text
          style={styles.compactDetail}
        >
          Avg {formatValue(metric, metric.average)}
          {"  •  "}
          {metric.sampleCount} samples
        </Text>
      </View>
    );
  }

  return (
    <View
      style={styles.card}
    >
      <View
        style={styles.header}
      >
        <View>
          <Text
            style={styles.eyebrow}
          >
            Latest
          </Text>

          <Text
            style={styles.title}
          >
            {metric.icon} {metric.title}
          </Text>
        </View>

        <View
          style={styles.sourcePill}
        >
          <Text
            style={styles.sourcePillText}
          >
            {metric.source}
          </Text>
        </View>
      </View>

      <Text
        style={styles.value}
      >
        {formatValue(
          metric,
          metric.latest,
        )}
      </Text>

      <View
        style={styles.statsRow}
      >
        <View
          style={styles.stat}
        >
          <Text
            style={styles.statLabel}
          >
            Today avg
          </Text>

          <Text
            style={styles.statValue}
          >
            {formatValue(
              metric,
              metric.average,
            )}
          </Text>
        </View>

        <View
          style={styles.stat}
        >
          <Text
            style={styles.statLabel}
          >
            Range
          </Text>

          <Text
            style={styles.statValue}
          >
            {
              metric.minimum === null
              || metric.maximum === null
                ? "No data"
                : (
                  `${formatValue(metric, metric.minimum)} – `
                  + `${formatValue(metric, metric.maximum)}`
                )
            }
          </Text>
        </View>

        <View
          style={styles.stat}
        >
          <Text
            style={styles.statLabel}
          >
            Samples
          </Text>

          <Text
            style={styles.statValue}
          >
            {metric.sampleCount}
          </Text>
        </View>
      </View>

      {
        metric.note
          ? (
            <Text
              style={styles.note}
            >
              {metric.note}
            </Text>
          )
          : null
      }
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
        borderRadius: 24,
        borderWidth: 1,
        padding: 18,
      },

      header: {
        alignItems: "flex-start",
        flexDirection: "row",
        justifyContent: "space-between",
      },

      eyebrow: {
        color: colors.textMuted,
        fontSize: 9,
        fontWeight: "700",
        letterSpacing: 0.8,
        textTransform: "uppercase",
      },

      title: {
        color: colors.heading,
        fontSize: 14,
        fontWeight: "800",
        marginTop: 3,
      },

      sourcePill: {
        backgroundColor: colors.accentSoft,
        borderRadius: 999,
        paddingHorizontal: 9,
        paddingVertical: 5,
      },

      sourcePillText: {
        color: colors.accent,
        fontSize: 9,
        fontWeight: "800",
      },

      value: {
        color: colors.text,
        fontSize: 34,
        fontWeight: "800",
        letterSpacing: -0.8,
        marginTop: 18,
      },

      statsRow: {
        borderColor: colors.border,
        borderTopWidth: 1,
        flexDirection: "row",
        gap: 8,
        marginTop: 15,
        paddingTop: 14,
      },

      stat: {
        flex: 1,
      },

      statLabel: {
        color: colors.textMuted,
        fontSize: 9,
        marginBottom: 4,
      },

      statValue: {
        color: colors.text,
        fontSize: 10,
        fontWeight: "700",
        lineHeight: 14,
      },

      note: {
        color: colors.textMuted,
        fontSize: 10,
        lineHeight: 16,
        marginTop: 13,
      },

      compactCard: {
        backgroundColor: colors.surface,
        borderColor: colors.border,
        borderRadius: 18,
        borderWidth: 1,
        padding: 14,
      },

      compactHeader: {
        alignItems: "center",
        flexDirection: "row",
        justifyContent: "space-between",
      },

      compactTitle: {
        color: colors.textMuted,
        flex: 1,
        fontSize: 10,
        fontWeight: "700",
        paddingRight: 8,
      },

      source: {
        color: colors.textMuted,
        fontSize: 8,
      },

      compactValue: {
        color: colors.text,
        fontSize: 22,
        fontWeight: "800",
        marginTop: 9,
      },

      compactDetail: {
        color: colors.textMuted,
        fontSize: 9,
        marginTop: 4,
      },
    }
  );
}
