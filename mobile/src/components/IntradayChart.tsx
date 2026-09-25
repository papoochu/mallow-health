import React, {
  useMemo,
  useState,
} from "react";

import {
  LayoutChangeEvent,
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


type IntradayChartProps = {
  colors: ThemeColors;
  metric: TodayMetricSummary;
};


type ChartPoint = {
  x: number;
  y: number;
  value: number;
  timestamp: string;
};


function formatNumber(
  metric: TodayMetricSummary,
  value: number,
) {
  const number = (
    metric.id === "wrist_temperature"
      && value >= 0
      ? `+${value.toFixed(metric.decimals)}`
      : value.toFixed(
          metric.decimals
        )
  );

  return `${number} ${metric.unit}`;
}


function formatTime(
  value: string,
) {
  return new Date(
    value
  ).toLocaleTimeString(
    [],
    {
      hour: "numeric",
      minute: "2-digit",
    },
  );
}


export default function IntradayChart({
  colors,
  metric,
}: IntradayChartProps) {
  const styles = createStyles(
    colors
  );

  const [containerWidth, setContainerWidth] = useState(
    0
  );

  const chartHeight = 168;
  const chartWidth = Math.max(
    0,
    containerWidth - 64,
  );

  const geometry = useMemo(
    () => {
      if (
        metric.points.length === 0
        || chartWidth <= 0
      ) {
        return null;
      }

      const values = metric.points.map(
        (
          point
        ) => point.value
      );

      const rawMinimum = Math.min(
        ...values
      );

      const rawMaximum = Math.max(
        ...values
      );

      const rawRange = Math.max(
        rawMaximum - rawMinimum,
        0.001,
      );

      const padding = Math.max(
        rawRange * 0.14,
        Math.abs(
          rawMaximum
        ) * 0.01,
        0.05,
      );

      const minimum = (
        rawMinimum - padding
      );

      const maximum = (
        rawMaximum + padding
      );

      const range = (
        maximum - minimum
      );

      const usableHeight = (
        chartHeight - 24
      );

      const points: ChartPoint[] = metric.points.map(
        (
          point,
          index,
        ) => {
          const x = (
            metric.points.length === 1
              ? chartWidth / 2
              : (
                index
                / (
                  metric.points.length - 1
                )
                * chartWidth
              )
          );

          const normalized = (
            (
              point.value - minimum
            )
            / range
          );

          const y = (
            12
            + (
              1 - normalized
            )
            * usableHeight
          );

          return {
            x,
            y,
            value: point.value,
            timestamp: point.timestamp,
          };
        }
      );

      const average = (
        metric.average ?? rawMinimum
      );

      const averageY = (
        12
        + (
          1
          - (
            (
              average - minimum
            )
            / range
          )
        )
        * usableHeight
      );

      return {
        points,
        rawMinimum,
        rawMaximum,
        average,
        averageY,
      };
    },
    [
      chartWidth,
      metric,
    ],
  );


  const handleLayout = (
    event: LayoutChangeEvent
  ) => {
    setContainerWidth(
      event.nativeEvent.layout.width
    );
  };


  return (
    <View
      onLayout={handleLayout}
      style={styles.card}
    >
      <View
        style={styles.header}
      >
        <View>
          <Text
            style={styles.title}
          >
            Throughout today
          </Text>

          <Text
            style={styles.subtitle}
          >
            {metric.sampleCount} usable samples
          </Text>
        </View>

        {
          metric.average !== null
            ? (
              <View
                style={styles.averagePill}
              >
                <Text
                  style={styles.averagePillText}
                >
                  Avg {formatNumber(metric, metric.average)}
                </Text>
              </View>
            )
            : null
        }
      </View>

      {
        geometry === null
          ? (
            <View
              style={styles.empty}
            >
              <Text
                style={styles.emptyText}
              >
                Not enough samples to draw today's chart yet.
              </Text>
            </View>
          )
          : (
            <View
              style={styles.chartRow}
            >
              <View
                style={[
                  styles.axisColumn,
                  {
                    height: chartHeight,
                  },
                ]}
              >
                <Text
                  style={styles.axisText}
                >
                  {formatNumber(
                    metric,
                    geometry.rawMaximum,
                  )}
                </Text>

                <Text
                  style={styles.axisText}
                >
                  {formatNumber(
                    metric,
                    geometry.average,
                  )}
                </Text>

                <Text
                  style={styles.axisText}
                >
                  {formatNumber(
                    metric,
                    geometry.rawMinimum,
                  )}
                </Text>
              </View>

              <View
                style={[
                  styles.plot,
                  {
                    height: chartHeight,
                    width: chartWidth,
                  },
                ]}
              >
                <View
                  style={[
                    styles.gridLine,
                    {
                      top: 12,
                    },
                  ]}
                />

                <View
                  style={[
                    styles.averageLine,
                    {
                      top: geometry.averageY,
                    },
                  ]}
                />

                <View
                  style={[
                    styles.gridLine,
                    {
                      bottom: 12,
                    },
                  ]}
                />

                {
                  geometry.points
                    .slice(
                      0,
                      -1,
                    )
                    .map(
                      (
                        point,
                        index,
                      ) => {
                        const next = geometry.points[
                          index + 1
                        ];

                        const dx = (
                          next.x - point.x
                        );

                        const dy = (
                          next.y - point.y
                        );

                        const length = Math.sqrt(
                          dx ** 2
                          + dy ** 2
                        );

                        const angle = Math.atan2(
                          dy,
                          dx,
                        );

                        const centerX = (
                          (
                            point.x
                            + next.x
                          )
                          / 2
                        );

                        const centerY = (
                          (
                            point.y
                            + next.y
                          )
                          / 2
                        );

                        return (
                          <View
                            key={
                              `segment-${index}`
                            }
                            style={[
                              styles.segment,
                              {
                                left: (
                                  centerX
                                  - length / 2
                                ),
                                top: (
                                  centerY - 1
                                ),
                                transform: [
                                  {
                                    rotate: `${angle}rad`,
                                  },
                                ],
                                width: length,
                              },
                            ]}
                          />
                        );
                      }
                    )
                }

                {
                  geometry.points.map(
                    (
                      point,
                      index,
                    ) => (
                      <View
                        key={
                          `dot-${index}`
                        }
                        style={[
                          styles.dot,
                          {
                            left: (
                              point.x - 3
                            ),
                            top: (
                              point.y - 3
                            ),
                          },
                        ]}
                      />
                    )
                  )
                }

                <Text
                  style={[
                    styles.timeLabel,
                    styles.leftTime,
                  ]}
                >
                  {
                    formatTime(
                      geometry.points[
                        0
                      ].timestamp
                    )
                  }
                </Text>

                <Text
                  style={[
                    styles.timeLabel,
                    styles.rightTime,
                  ]}
                >
                  {
                    formatTime(
                      geometry.points[
                        geometry.points.length - 1
                      ].timestamp
                    )
                  }
                </Text>
              </View>
            </View>
          )
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
        marginTop: 12,
        padding: 16,
      },

      header: {
        alignItems: "flex-start",
        flexDirection: "row",
        justifyContent: "space-between",
        marginBottom: 14,
      },

      title: {
        color: colors.heading,
        fontSize: 14,
        fontWeight: "800",
      },

      subtitle: {
        color: colors.textMuted,
        fontSize: 9,
        marginTop: 3,
      },

      averagePill: {
        backgroundColor: colors.accentSoft,
        borderRadius: 999,
        paddingHorizontal: 9,
        paddingVertical: 5,
      },

      averagePillText: {
        color: colors.accent,
        fontSize: 8,
        fontWeight: "800",
      },

      chartRow: {
        flexDirection: "row",
      },

      axisColumn: {
        justifyContent: "space-between",
        paddingBottom: 8,
        paddingRight: 8,
        paddingTop: 5,
        width: 64,
      },

      axisText: {
        color: colors.text,
        fontSize: 8,
        fontWeight: "600",
        textAlign: "right",
      },

      plot: {
        position: "relative",
      },

      gridLine: {
        backgroundColor: colors.chartMuted,
        height: 1,
        left: 0,
        opacity: 0.75,
        position: "absolute",
        right: 0,
      },

      averageLine: {
        backgroundColor: colors.pink,
        height: 1,
        left: 0,
        opacity: 0.65,
        position: "absolute",
        right: 0,
      },

      segment: {
        backgroundColor: colors.chartLine,
        borderRadius: 999,
        height: 2,
        position: "absolute",
      },

      dot: {
        backgroundColor: colors.chartLine,
        borderColor: colors.surface,
        borderRadius: 999,
        borderWidth: 1,
        height: 7,
        position: "absolute",
        width: 7,
      },

      timeLabel: {
        bottom: -2,
        color: colors.textMuted,
        fontSize: 8,
        position: "absolute",
      },

      leftTime: {
        left: 0,
      },

      rightTime: {
        right: 0,
      },

      empty: {
        alignItems: "center",
        justifyContent: "center",
        minHeight: 150,
      },

      emptyText: {
        color: colors.textMuted,
        fontSize: 11,
        lineHeight: 17,
        textAlign: "center",
      },
    }
  );
}
