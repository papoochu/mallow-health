import React from "react";

import {
  ActivityIndicator,
  Pressable,
  StyleSheet,
  Text,
  View,
} from "react-native";

import {
  ThemeColors,
} from "../theme/colors";


type LoadingStateProps = {
  colors: ThemeColors;
};


export function LoadingState({
  colors,
}: LoadingStateProps) {
  const styles = createStyles(
    colors
  );

  return (
    <View
      style={styles.center}
    >
      <ActivityIndicator
        color={colors.accent}
        size="large"
      />

      <Text
        style={styles.message}
      >
        Loading your health data…
      </Text>
    </View>
  );
}


type ErrorStateProps = {
  colors: ThemeColors;
  message: string;
  onRetry: () => void;
};


export function ErrorState({
  colors,
  message,
  onRetry,
}: ErrorStateProps) {
  const styles = createStyles(
    colors
  );

  return (
    <View
      style={styles.center}
    >
      <Text
        style={styles.errorTitle}
      >
        Mallow couldn’t load the data.
      </Text>

      <Text
        style={styles.message}
      >
        {message}
      </Text>

      <Pressable
        onPress={onRetry}
        style={styles.retryButton}
      >
        <Text
          style={styles.retryText}
        >
          Try again
        </Text>
      </Pressable>
    </View>
  );
}


function createStyles(
  colors: ThemeColors,
) {
  return StyleSheet.create(
    {
      center: {
        alignItems: "center",
        flex: 1,
        justifyContent: "center",
        paddingHorizontal: 28,
      },

      errorTitle: {
        color: colors.text,
        fontSize: 17,
        fontWeight: "800",
        marginBottom: 8,
        textAlign: "center",
      },

      message: {
        color: colors.textMuted,
        fontSize: 12,
        lineHeight: 18,
        marginTop: 10,
        textAlign: "center",
      },

      retryButton: {
        backgroundColor: colors.input,
        borderRadius: 15,
        marginTop: 18,
        paddingHorizontal: 18,
        paddingVertical: 11,
      },

      retryText: {
        color: colors.inputText,
        fontSize: 12,
        fontWeight: "800",
      },
    }
  );
}
