import React, {
  useState,
} from "react";

import {
  KeyboardAvoidingView,
  Platform,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  View,
} from "react-native";

import ScreenHeader from "../components/ScreenHeader";

import {
  useHealthData,
} from "../data/HealthDataContext";

import {
  ThemeColors,
} from "../theme/colors";


type AskScreenProps = {
  colors: ThemeColors;
  darkMode: boolean;
  onToggleDarkMode: () => void;
};


const suggestions = [
  "How has my HRV changed this month?",
  "What is related to my sleep?",
  "How does this week compare with last week for resting heart rate?",
];


export default function AskScreen({
  colors,
  darkMode,
  onToggleDarkMode,
}: AskScreenProps) {
  const {
    ask,
  } = useHealthData();

  const [question, setQuestion] = useState(
    ""
  );

  const [answer, setAnswer] = useState(
    ""
  );

  const [asking, setAsking] = useState(
    false
  );

  const styles = createStyles(
    colors
  );


  const submitQuestion = async (
    value?: string
  ) => {
    const text = (
      value ?? question
    ).trim();

    if (
      !text
      || asking
    ) {
      return;
    }

    setQuestion(
      text
    );

    setAsking(
      true
    );

    try {
      const response = await ask(
        text
      );

      setAnswer(
        response
      );
    } catch (
      caught
    ) {
      setAnswer(
        caught instanceof Error
          ? (
            "Mallow couldn't analyze that question: "
            + caught.message
          )
          : "Mallow couldn't analyze that question right now."
      );
    } finally {
      setAsking(
        false
      );
    }
  };


  return (
    <KeyboardAvoidingView
      style={styles.root}
      behavior={
        Platform.OS === "ios"
          ? "padding"
          : undefined
      }
    >
      <ScrollView
        style={styles.scroll}
        contentContainerStyle={styles.content}
        keyboardShouldPersistTaps="handled"
        showsVerticalScrollIndicator={false}
      >
        <ScreenHeader
          colors={colors}
          darkMode={darkMode}
          onToggleDarkMode={onToggleDarkMode}
          title="Ask Mallow 💬"
          subtitle="explore your health data in plain language"
        />

        <View
          style={styles.introCard}
        >
          <Text
            style={styles.introTitle}
          >
            What would you like to explore?
          </Text>

          <Text
            style={styles.introBody}
          >
            Ask about recent values, trends, comparisons, unusual patterns,
            or relationships between measurements.
          </Text>
        </View>

        <View
          style={styles.inputCard}
        >
          <TextInput
            value={question}
            onChangeText={setQuestion}
            placeholder="Ask about your health data..."
            placeholderTextColor={colors.textMuted}
            multiline
            style={styles.input}
          />

          <Pressable
            disabled={asking}
            onPress={() => {
              void submitQuestion();
            }}
            style={[
              styles.askButton,
              asking
                ? styles.askButtonDisabled
                : null,
            ]}
          >
            <Text
              style={styles.askButtonText}
            >
              {
                asking
                  ? "Analyzing…"
                  : "Ask Mallow"
              }
            </Text>
          </Pressable>
        </View>

        <Text
          style={styles.suggestionHeading}
        >
          Try asking
        </Text>

        <View
          style={styles.suggestions}
        >
          {
            suggestions.map(
              (
                suggestion
              ) => (
                <Pressable
                  key={suggestion}
                  disabled={asking}
                  onPress={() => {
                    void submitQuestion(
                      suggestion
                    );
                  }}
                  style={styles.suggestion}
                >
                  <Text
                    style={styles.suggestionText}
                  >
                    {suggestion}
                  </Text>
                </Pressable>
              )
            )
          }
        </View>

        {
          answer
            ? (
              <View
                style={styles.answerCard}
              >
                <Text
                  style={styles.answerLabel}
                >
                  Mallow 🌿
                </Text>

                <Text
                  style={styles.answerText}
                >
                  {answer}
                </Text>
              </View>
            )
            : null
        }

        <Text
          style={styles.disclaimer}
        >
          Ask Mallow summarizes statistical patterns in the available
          personal data. It does not provide diagnosis, treatment, or
          emergency medical advice.
        </Text>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}


function createStyles(
  colors: ThemeColors,
) {
  return StyleSheet.create(
    {
      root: {
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

      introCard: {
        backgroundColor: colors.surfaceSoft,
        borderColor: colors.border,
        borderRadius: 24,
        borderWidth: 1,
        padding: 20,
      },

      introTitle: {
        color: colors.text,
        fontSize: 20,
        fontWeight: "800",
      },

      introBody: {
        color: colors.textMuted,
        fontSize: 12,
        lineHeight: 19,
        marginTop: 8,
      },

      inputCard: {
        backgroundColor: colors.surface,
        borderColor: colors.border,
        borderRadius: 22,
        borderWidth: 1,
        marginTop: 16,
        padding: 14,
      },

      input: {
        color: colors.text,
        fontSize: 14,
        minHeight: 88,
        padding: 4,
        textAlignVertical: "top",
      },

      askButton: {
        alignItems: "center",
        backgroundColor: colors.input,
        borderRadius: 16,
        marginTop: 10,
        paddingVertical: 13,
      },

      askButtonDisabled: {
        opacity: 0.65,
      },

      askButtonText: {
        color: colors.inputText,
        fontSize: 13,
        fontWeight: "800",
      },

      suggestionHeading: {
        color: colors.heading,
        fontSize: 16,
        fontWeight: "800",
        marginBottom: 10,
        marginTop: 22,
      },

      suggestions: {
        gap: 8,
      },

      suggestion: {
        backgroundColor: colors.surface,
        borderColor: colors.border,
        borderRadius: 17,
        borderWidth: 1,
        paddingHorizontal: 14,
        paddingVertical: 13,
      },

      suggestionText: {
        color: colors.text,
        fontSize: 12,
      },

      answerCard: {
        backgroundColor: colors.pinkSoft,
        borderColor: colors.border,
        borderRadius: 22,
        borderWidth: 1,
        marginTop: 18,
        padding: 18,
      },

      answerLabel: {
        color: colors.heading,
        fontSize: 13,
        fontWeight: "800",
        marginBottom: 8,
      },

      answerText: {
        color: colors.text,
        fontSize: 12,
        lineHeight: 19,
      },

      disclaimer: {
        color: colors.textMuted,
        fontSize: 10,
        lineHeight: 16,
        marginTop: 22,
        textAlign: "center",
      },
    }
  );
}
