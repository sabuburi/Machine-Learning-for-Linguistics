# ================================================================
# Jiwar — Full pipeline: surprisal/entropy, regressions, plots (JPEG)
# with full language names in outputs
#
# EDIT: affricates and diphthongs are now treated as single phonemic
# units on a per-language basis (see `lang_units` / `build_lang_pattern`),
# rather than using one generic digraph pattern for every language.
# ================================================================

#####Preamble#####
library(conflicted)
library(readr)
library(dplyr)
library(tidyr)
library(stringr)
library(purrr)
library(tibble)
library(progress)
library(broom)
library(ggplot2)
library(RColorBrewer)

conflicts_prefer(dplyr::select)
conflicts_prefer(dplyr::filter)

#####Language list and names#####
all_codes <- c("ar")

lang_names <- c(
  "af" = "Afrikaans", "ar" = "Arabic", "bg" = "Bulgarian",
  "bs" = "Bosnian", "ca" = "Catalan", "cs" = "Czech",
  "de" = "German", "el" = "Greek", "en-gb" = "English (GB)",
  "en-us" = "English (US)", "eo" = "Esperanto", "es" = "Spanish",
  "et" = "Estonian", "eu" = "Basque", "fa" = "Persian",
  "fi" = "Finnish", "fr" = "French", "hr" = "Croatian",
  "hu" = "Hungarian", "hy" = "Armenian", "id" = "Indonesian",
  "it" = "Italian", "kk" = "Kazakh", "ko" = "Korean",
  "lt" = "Lithuanian", "lv" = "Latvian", "mk" = "Macedonian",
  "ms" = "Malay", "nl" = "Dutch", "no" = "Norwegian",
  "pl" = "Polish", "pt" = "Portuguese", "ro" = "Romanian",
  "ru" = "Russian", "sk" = "Slovak", "sq" = "Albanian",
  "sr" = "Serbian", "sv" = "Swedish", "tr" = "Turkish",
  "uk" = "Ukrainian", "ur" = "Urdu"
)

base_url <- "https://raw.githubusercontent.com/AlaaAlzahrani/Jiwar_database/master/jiwar_database/csv/"

#####Helper: download & read#####
get_jiwar <- function(code) {
  dest_file <- file.path("data_raw", paste0(code, "_subs.csv"))
  dir.create("data_raw", showWarnings = FALSE)
  if (!file.exists(dest_file)) {
    url <- paste0(base_url, code, "_subs.csv")
    download.file(url, destfile = dest_file, mode = "wb", quiet = TRUE)
  }
  read_csv(dest_file, locale = locale(encoding = "UTF-8"), show_col_types = FALSE)
}

#####IPA segmentation#####
##### Per-language multi-character units (affricates + diphthongs) #####

lang_units <- list(
  af      = c("əi","əu","øy","ɑɪ","ʊɪ","uɪ","iuː","aɪ","ɔɪ"),
  ar      = c("aw","aj"),
  bg      = c("ts","dz","tʃ","dʒ"),
  bs      = c("ts","dʒ","tʃ","tɕ","dʑ"),
  ca      = c("ts","dz","tɕ","dʑ"),
  cs      = c("aʊ","eʊ","oʊ"),
  de      = c("aɪ","aʊ","ɔø","pf","ts","tʃ","dʒ"),
  `en-gb` = c("tʃ","dʒ","eɪ","aɪ","ɔɪ","aʊ","əʊ","eə","iə","ʊə"),
  `en-us` = c("tʃ","dʒ","eɪ","aɪ","ɔɪ","aʊ","oʊ","ɪə","eə"),
  eo      = c("tʃ","dʒ","ts"),
  es      = c("tʃ","ja","je","jo","ju","wa","we","wo","wi","aɪ","aw","eɪ","ew","oɪ"),
  et      = c("ai","ae","æi","ei","au","ea","oi","ui","oe","ɵi","iu","øi","æe","ue","yi","oaː"),
  eu      = c("aɪ","eɪ","oɪ","aʊ","eʊ","ui","ts̻","ts̺","tʃ"),
  fa      = c("tʃ","dʒ"),
  hr      = c("ts","tʃ","tɕ","dʒ","dʑ"),
  hu      = c("ts","tʃ","dʒ","dzː"),
  hy      = c("ts","dz","tsʰ","tʃ","dʒ","tʃʰ"),
  it      = c("ts","dz","tʃ","dʒ"),
  ko      = c("ɯj","tɕ","tʃ","dʑ","ts"),
  lt      = c("ts","dz","tɕ","tʃ","dʑ","dʒ","ai","au","eɪ","ui","ie","uo"),
  lv      = c("ts","dz","tʃ","dʒ","ai","ui","au","ie","iu"),
  mk      = c("ts","dz","dʒ","dʑ","tɕ"),
  ms      = c("dʒ","tʃ"),
  nl      = c("dʒ","tʃ","kj","ɛɪ","œy","ʌʊ"),
  no      = c("aɪ","øy","aʊ"),
  pl      = c("ts","dʑ","tɕ","tʃ","dʒ"),
  pt      = c("aɪ","eɪ","aʊ","ɛʊ","ɐ̃j","õj","uɪ","ɐ̃ʊ̃"),
  ro      = c("ts","tʃ","dʒ","ea","ɔa"),
  ru      = c("ts","tɕ"),
  sk      = c("ts","dʑ","tʃ","dʒ","ia","ie","iu","uo"),
  sq      = c("ts","dʑ","tʃ","dʒ","tɕ","aɪ","jɛ","uɛ"),
  sr      = c("ts","dʑ","tʃ","dʒ","tɕ"),
  tr      = c("tʃ","dʒ"),
  uk      = c("tʃ","dʒ","dz","ts"),
  ur      = c("tʃ","aːi","aːoː","aːʋ","oːi")
  # el, fi, fr, id, kk, sv intentionally absent — no multi-char units
)

diacritics <- c(
  "ː", "ˤ", "̃", "̪", "̟", "̠", "̈", "ˁ", "ˀ", "ʼ",
  "̥", "̬", "̰", "̤", "̺", "̻", "̞", "̝", "̹", "̜",
  "̘", "̙", "̚", "ʲ", "ʰ")

ipa_letters <- "[A-Za-z\u0250-\u02AF]"

diacritic_pattern <- paste0(
  "[",
  paste(diacritics, collapse = ""),
  "]*"
)

# Escape regex metacharacters in literal IPA strings before building alternation
escape_regex <- function(x) {
  stringr::str_replace_all(x, "([\\^\\$\\.\\|\\?\\*\\+\\(\\)\\[\\]\\{\\}\\\\])", "\\\\\\1")
}

# Build a language-specific extraction pattern. Longer units MUST come first
# in the alternation so e.g. "tsʰ" is matched before "ts", "ea" before a bare
# "e", etc. Languages with no listed units fall back to plain IPA letters.
build_lang_pattern <- function(code) {
  units <- unique(lang_units[[code]])
  if (!is.null(units) && length(units) > 0) {
    units_sorted  <- units[order(-nchar(units))]
    units_escaped <- escape_regex(units_sorted)
    unit_alt <- paste0("(", paste(units_escaped, collapse = "|"), ")")
    paste0(unit_alt, diacritic_pattern, "|", ipa_letters, diacritic_pattern)
  } else {
    paste0(ipa_letters, diacritic_pattern)
  }
}

# General segmentation — takes the language-specific pattern as an argument
segment_ipa <- function(ipa_string, pattern) {
  if (is.na(ipa_string)) return(character(0))

  clean <- str_remove_all(ipa_string, "[\u02c8\u02cc.]")

  str_extract_all(
    clean,
    pattern
  )[[1]]
}

#####Process one language#####
process_language <- function(code) {
  message("Processing: ", code)
  raw_df <- get_jiwar(code)
  clean_df <- raw_df %>%
    filter(!is.na(IPA), !is.na(raw_frequency))
  if (nrow(clean_df) == 0) {
    message("   No valid words for ", code, " – skipping")
    return(NULL)
  }

  pattern <- build_lang_pattern(code)

  clean_df <- clean_df %>%
    mutate(phonemes = map(IPA, ~ segment_ipa(.x, pattern)),
           n_phon   = lengths(phonemes)) %>%
    filter(n_phon >= 2)
  if (nrow(clean_df) == 0) {
    message("   No words with >=2 phonemes for ", code, " – skipping")
    return(NULL)
  }
  max_phon <- max(clean_df$n_phon)

  phoneme_long <- clean_df %>%
    select(word, raw_frequency, phonemes) %>%
    mutate(row_id = row_number()) %>%
    unnest(phonemes) %>%
    group_by(row_id) %>%
    mutate(position = row_number()) %>%
    ungroup() %>%
    rename(phoneme = phonemes)

  bigram_long <- phoneme_long %>%
    group_by(row_id) %>%
    mutate(phoneme_next = lead(phoneme)) %>%
    ungroup() %>%
    filter(!is.na(phoneme_next)) %>%
    mutate(bigram = paste(phoneme, phoneme_next, sep = "_"))

  bigram_counts <- bigram_long %>%
    group_by(bigram, phoneme) %>%
    summarize(Sum_Total = sum(raw_frequency), .groups = "drop") %>%
    rename(Left_of_Underscore = phoneme)

  sum_by_category <- bigram_counts %>%
    group_by(Left_of_Underscore) %>%
    summarize(Category_Total = sum(Sum_Total), .groups = "drop")

  sum_totals_df <- bigram_counts %>%
    left_join(sum_by_category, by = "Left_of_Underscore") %>%
    mutate(Divided_Sum = Sum_Total / Category_Total,
           Surprisal   = -log2(Divided_Sum)) %>%
    select(bigram, Sum_Total, Left_of_Underscore, Divided_Sum, Surprisal)

  entropy <- sum_totals_df %>%
    group_by(Left_of_Underscore) %>%
    summarize(Entropy = -sum(Divided_Sum * log2(Divided_Sum), na.rm = TRUE),
              .groups = "drop") %>%
    arrange(desc(Entropy))

  surprisal_lookup <- setNames(sum_totals_df$Surprisal, sum_totals_df$bigram)
  entropy_lookup   <- setNames(entropy$Entropy, entropy$Left_of_Underscore)

  bigram_long <- bigram_long %>%
    mutate(surprisal_value = surprisal_lookup[bigram])
  phoneme_long <- phoneme_long %>%
    mutate(entropy_value = entropy_lookup[phoneme])

  surprisal_wide <- bigram_long %>%
    select(row_id, position, surprisal_value) %>%
    mutate(col = paste0("S", position)) %>%
    select(row_id, col, surprisal_value) %>%
    pivot_wider(names_from = col, values_from = surprisal_value)

  entropy_wide <- phoneme_long %>%
    select(row_id, position, entropy_value) %>%
    mutate(col = paste0("E", position)) %>%
    select(row_id, col, entropy_value) %>%
    pivot_wider(names_from = col, values_from = entropy_value)

  word_lookup <- clean_df %>%
    mutate(row_id = row_number(),
           phonemes_str = map_chr(phonemes, paste, collapse = " ")) %>%
    select(-phonemes)

  word_sequence <- word_lookup %>%
    left_join(surprisal_wide, by = "row_id") %>%
    left_join(entropy_wide, by = "row_id") %>%
    select(-row_id)

  s_cols <- paste0("S", 1:(max_phon - 1))
  e_cols <- paste0("E", 1:max_phon)
  s_cols <- s_cols[s_cols %in% names(word_sequence)]
  e_cols <- e_cols[e_cols %in% names(word_sequence)]

  word_summary <- word_sequence %>%
    rowwise() %>%
    mutate(
      First_Surprisal   = first(na.omit(c_across(all_of(s_cols)))),
      Last_Surprisal    = last(na.omit(c_across(all_of(s_cols)))),
      Average_Surprisal = mean(c_across(all_of(s_cols)), na.rm = TRUE),
      Max_Surprisal     = max(c_across(all_of(s_cols)), na.rm = TRUE),
      First_Entropy   = first(na.omit(c_across(all_of(e_cols)))),
      Last_Entropy    = last(na.omit(c_across(all_of(e_cols)))),
      Average_Entropy = mean(c_across(all_of(e_cols)), na.rm = TRUE),
      Max_Entropy     = max(c_across(all_of(e_cols)), na.rm = TRUE)
    ) %>%
    ungroup() %>%
    select(word, First_Surprisal, Last_Surprisal, Average_Surprisal, Max_Surprisal,
           First_Entropy, Last_Entropy, Average_Entropy, Max_Entropy)

  orig_cols <- names(raw_df)
  final_output <- word_sequence %>%
    left_join(word_summary, by = "word") %>%
    select(all_of(orig_cols),
           n_phon, phonemes_str,
           all_of(s_cols), all_of(e_cols),
           First_Surprisal, Last_Surprisal, Average_Surprisal, Max_Surprisal,
           First_Entropy, Last_Entropy, Average_Entropy, Max_Entropy)

  dir.create("outputs", showWarnings = FALSE)
  write_csv(final_output, file.path("outputs", paste0(code, "_comprehensive.csv")))
  write_csv(sum_totals_df, file.path("outputs", paste0(code, "_bigram_lookup.csv")))
  write_csv(entropy,       file.path("outputs", paste0(code, "_phoneme_entropy.csv")))

  message("   ✅ Done – saved to outputs/", code, "_comprehensive.csv")
  return(final_output)
}

#####Run all languages#####
dir.create("outputs", showWarnings = FALSE)
pb <- progress_bar$new(total = length(all_codes), format = "  Processing [:bar] :percent eta: :eta")
results <- list()
for (code in all_codes) {
  pb$tick()
  res <- tryCatch({
    process_language(code)
  }, error = function(e) {
    message("\n   ❌ Error processing ", code, ": ", e$message)
    NULL
  })
  results[[code]] <- res
}

#####Summary and counts (with full names)#####
successful <- names(results)[!sapply(results, is.null)]
failed <- setdiff(all_codes, successful)

cat("\n====================================\n")
cat("Processed", length(successful), "languages successfully.\n")
if (length(failed) > 0) {
  cat("Failed (or no valid words):", paste(failed, collapse = ", "), "\n")
}
cat("Output files are in the 'outputs' folder.\n")

if (length(successful) > 0) {
  count_table <- map_dfr(successful, function(code) {
    df <- results[[code]]
    tibble(
      Language = lang_names[code],
      Types = nrow(df),
      Tokens = sum(df$raw_frequency, na.rm = TRUE)
    )
  }) %>%
    bind_rows(tibble(
      Language = "TOTAL",
      Types = sum(.$Types),
      Tokens = sum(.$Tokens)
    ))
  cat("\n====================================\n")
  cat("Word counts per language:\n")
  print(count_table)
  write_csv(count_table, "outputs/word_counts.csv")
  cat("\nCount table saved to outputs/word_counts.csv\n")
} else {
  cat("\nNo languages were processed successfully.\n")
}

#####Regressions: S&E metrics ~ n_phon#####
cat("\n====================================\n")
cat("Running regressions: S&E metrics ~ n_phon\n")

files <- file.path("outputs", paste0(all_codes, "_comprehensive.csv"))
codes <- gsub("_comprehensive\\.csv$", "", basename(files))
metrics <- c("First_Surprisal", "Last_Surprisal", "Average_Surprisal", "Max_Surprisal",
             "First_Entropy",   "Last_Entropy",   "Average_Entropy",   "Max_Entropy")

regress_language <- function(file, code) {
  df <- read_csv(file, show_col_types = FALSE)
  if (!"n_phon" %in% names(df)) {
    warning(code, ": missing n_phon; skipping")
    return(NULL)
  }
  available_metrics <- intersect(metrics, names(df))
  if (length(available_metrics) == 0) {
    warning(code, ": no S&E metrics available; skipping")
    return(NULL)
  }
  vars <- c("n_phon", available_metrics)
  df_clean <- df %>% select(all_of(vars)) %>% na.omit()
  if (nrow(df_clean) < 3) {
    warning(code, ": too few complete cases; skipping")
    return(NULL)
  }
  results <- map_dfr(available_metrics, function(m) {
    model <- lm(as.formula(paste(m, "~ n_phon")), data = df_clean)
    tidy_model <- tidy(model)
    glance_model <- glance(model)
    tibble(
      language = code,
      full_language = lang_names[code],
      metric = m,
      intercept = tidy_model$estimate[1],
      slope = tidy_model$estimate[2],
      r_squared = glance_model$r.squared,
      p_value = glance_model$p.value
    )
  })
  return(results)
}

all_regressions <- map2_df(files, codes, ~ regress_language(.x, .y))
write_csv(all_regressions, "outputs/regressions_S&E_vs_n_phon.csv")

summary_stats <- all_regressions %>%
  group_by(metric) %>%
  summarise(
    mean_slope = mean(slope, na.rm = TRUE),
    sd_slope = sd(slope, na.rm = TRUE),
    se_slope = sd_slope / sqrt(n()),
    ci_lower = mean_slope - qt(0.975, df = n() - 1) * se_slope,
    ci_upper = mean_slope + qt(0.975, df = n() - 1) * se_slope,

    median_slope = median(slope, na.rm = TRUE),
    min_slope = min(slope, na.rm = TRUE),
    max_slope = max(slope, na.rm = TRUE),

    mean_r2 = mean(r_squared, na.rm = TRUE),
    sd_r2 = sd(r_squared, na.rm = TRUE),

    positive_slopes = sum(slope > 0, na.rm = TRUE),
    negative_slopes = sum(slope < 0, na.rm = TRUE),
    significant = sum(p_value < .05, na.rm = TRUE),
    non_significant = sum(p_value >= .05, na.rm = TRUE),

    n_languages = n(),
    .groups = "drop"
  ) %>%
  arrange(desc(abs(mean_slope)))

write_csv(summary_stats,
          "outputs/regression_summary_across_languages.csv")

cat("\nSummary across languages:\n")
print(summary_stats)

cat("\nFull regression table saved to:\n")
cat("outputs/regressions_S&E_vs_n_phon.csv\n")

cat("\nSummary table saved to:\n")
cat("outputs/regression_summary_across_languages.csv\n")

#####Plots: Average Surprisal by length (JPEG)#####
cat("\n====================================\n")
cat("Generating Average Surprisal by length plots (JPEG)\n")

files <- file.path("outputs", paste0(all_codes, "_comprehensive.csv"))
codes <- gsub("_comprehensive\\.csv$", "", basename(files))

compute_summary <- function(file, code) {
  df <- read_csv(file, show_col_types = FALSE)
  if (!all(c("n_phon", "Average_Surprisal") %in% names(df))) {
    warning(code, ": missing columns; skipping")
    return(NULL)
  }
  df_filt <- df %>%
    filter(n_phon %in% 3:8) %>%
    select(n_phon, Average_Surprisal) %>%
    na.omit()
  if (nrow(df_filt) == 0) {
    warning(code, ": no data for lengths 3–8; skipping")
    return(NULL)
  }
  summary_df <- df_filt %>%
    group_by(n_phon) %>%
    summarise(
      N = n(),
      mean = mean(Average_Surprisal),
      sd = sd(Average_Surprisal),
      se = sd / sqrt(N),
      ci_lower = mean - qt(0.975, df = N - 1) * se,
      ci_upper = mean + qt(0.975, df = N - 1) * se,
      .groups = "drop"
    ) %>%
    mutate(language = code,
           full_language = lang_names[code])
  return(summary_df)
}

all_summaries <- map2_df(files, codes, ~ compute_summary(.x, .y))
write_csv(all_summaries, "outputs/surprisal_by_length_summary.csv")

length_colours <- setNames(brewer.pal(6, "Set1"), 3:8)

# Individual plots with full names in titles
plot_list <- list()
for (lang in codes) {
  lang_data <- all_summaries %>% filter(language == lang)
  if (nrow(lang_data) == 0) next
  p <- ggplot(lang_data, aes(x = factor(n_phon), y = mean,
                             colour = factor(n_phon), group = 1)) +
    geom_point(size = 3) +
    geom_errorbar(aes(ymin = ci_lower, ymax = ci_upper), width = 0.2, size = 1) +
    scale_colour_manual(values = length_colours[as.character(3:8)]) +
    geom_text(aes(label = paste0("N=", N)), vjust = -1, size = 3, colour = "black") +
    labs(title = paste(lang_names[lang], "– Average Surprisal by Phoneme Length"),
         x = "Phoneme Length (n_phon)", y = "Average Surprisal (bits)",
         colour = "Length") +
    theme_minimal(base_size = 14) +
    theme(legend.position = "bottom")
  plot_list[[lang]] <- p
}
if (length(plot_list) > 0) {
  for (lang in names(plot_list)) {
    ggsave(filename = paste0("outputs/surprisal_by_length_", lang, ".jpg"),
           plot = plot_list[[lang]], width = 10, height = 7, dpi = 300)
  }
  cat("Plots saved as JPEGs in outputs/ (surprisal_by_length_*.jpg)\n")
} else {
  cat("No plots generated for Average Surprisal by length.\n")
}

# Faceted version with full names
if (nrow(all_summaries) > 0) {
  all_summaries$n_phon <- factor(all_summaries$n_phon)
  avg_faceted <- ggplot(all_summaries, aes(x = n_phon, y = mean,
                                           colour = n_phon, group = 1)) +
    geom_point(size = 2) +
    geom_errorbar(aes(ymin = ci_lower, ymax = ci_upper), width = 0.2, size = 0.8) +
    scale_colour_manual(values = length_colours[as.character(3:8)]) +
    facet_wrap(~ full_language, scales = "free_y", ncol = 5) +
    labs(x = "Phoneme Length", y = "Average Surprisal (bits)", colour = "Length") +
    theme_minimal(base_size = 10) +
    theme(legend.position = "bottom")
  ggsave("outputs/surprisal_by_length_faceted.jpg", avg_faceted,
         width = 16, height = 12, dpi = 300)
  cat("Saved faceted plot to outputs/surprisal_by_length_faceted.jpg\n")
}

#####Plots: Positional Surprisal by length (JPEG)#####
cat("\n====================================\n")
cat("Generating Positional Surprisal profiles (JPEG)\n")

files <- file.path("outputs", paste0(all_codes, "_comprehensive.csv"))
codes <- gsub("_comprehensive\\.csv$", "", basename(files))

compute_positional_summary <- function(file, code) {
  df <- read_csv(file, show_col_types = FALSE)
  if (!"n_phon" %in% names(df)) return(tibble())
  s_cols <- grep("^S[0-9]+$", names(df), value = TRUE)
  if (length(s_cols) == 0) return(tibble())
  df_filt <- df %>%
    filter(n_phon %in% 3:8) %>%
    select(n_phon, all_of(s_cols))
  if (nrow(df_filt) == 0) return(tibble())
  long_df <- df_filt %>%
    pivot_longer(cols = all_of(s_cols), names_to = "pos", values_to = "surprisal",
                 values_drop_na = TRUE) %>%
    mutate(position = as.numeric(gsub("S", "", pos))) %>%
    select(-pos)
  if (nrow(long_df) == 0) return(tibble())
  summary_df <- long_df %>%
    group_by(n_phon, position) %>%
    summarise(
      N = n(),
      mean = mean(surprisal, na.rm = TRUE),
      sd = sd(surprisal, na.rm = TRUE),
      .groups = "drop"
    ) %>%
    mutate(
      se = ifelse(N > 1, sd / sqrt(N), NA_real_),
      ci_lower = ifelse(N > 1, mean - qt(0.975, df = N - 1) * se, NA_real_),
      ci_upper = ifelse(N > 1, mean + qt(0.975, df = N - 1) * se, NA_real_)
    ) %>%
    mutate(language = code,
           full_language = lang_names[code])
  return(summary_df)
}

all_positional <- map2_df(files, codes, ~ compute_positional_summary(.x, .y))

if (nrow(all_positional) == 0) {
  cat("No positional summary data – skipping positional plots.\n")
} else {
  write_csv(all_positional, "outputs/positional_surprisal_summary.csv")

  length_colours <- setNames(brewer.pal(6, "Set1"), 3:8)

  plot_language <- function(lang) {
    lang_data <- all_positional %>% filter(language == lang)
    if (nrow(lang_data) == 0) return(NULL)
    lang_data$position <- as.numeric(lang_data$position)
    ggplot(lang_data, aes(x = position, y = mean,
                          colour = factor(n_phon), fill = factor(n_phon))) +
      geom_line(size = 1.2) +
      geom_ribbon(aes(ymin = ci_lower, ymax = ci_upper), alpha = 0.2, colour = NA) +
      scale_colour_manual(values = length_colours[as.character(3:8)]) +
      scale_fill_manual(values = length_colours[as.character(3:8)]) +
      labs(title = paste(lang_names[lang], "– Positional Surprisal by Word Length"),
           x = "Bigram Position", y = "Mean Surprisal (bits)",
           colour = "Length", fill = "Length") +
      theme_minimal(base_size = 14) + theme(legend.position = "bottom")
  }

  plot_list <- map(unique(all_positional$language), plot_language)
  plot_list <- compact(plot_list)

  if (length(plot_list) > 0) {
    for (lang in names(plot_list)) {
      ggsave(filename = paste0("outputs/positional_surprisal_", lang, ".jpg"),
             plot = plot_list[[lang]], width = 10, height = 7, dpi = 300)
    }
    cat("Saved individual plots as JPEGs in outputs/ (positional_surprisal_*.jpg)\n")
  }

  # Faceted overview (JPEG) with full names
  if (exists("all_positional") && nrow(all_positional) > 0) {
    all_positional$position <- as.numeric(all_positional$position)

    if (!exists("length_colours")) {
      length_colours <- setNames(brewer.pal(6, "Set1"), 3:8)
    }

    faceted <- ggplot(all_positional, aes(x = position, y = mean,
                                          colour = factor(n_phon), fill = factor(n_phon))) +
      geom_line(size = 1) +
      geom_ribbon(aes(ymin = ci_lower, ymax = ci_upper), alpha = 0.15, colour = NA) +
      scale_colour_manual(values = length_colours[as.character(3:8)]) +
      scale_fill_manual(values = length_colours[as.character(3:8)]) +
      facet_wrap(~ full_language, scales = "free_y", ncol = 5) +
      labs(x = "Bigram Position", y = "Mean Surprisal (bits)", colour = "Phoneme Length") +
      theme_minimal(base_size = 10) +
      theme(legend.position = "bottom")

    ggsave("outputs/positional_surprisal_faceted.jpg", faceted,
           width = 16, height = 12, dpi = 300)
    cat("Saved faceted plot to outputs/positional_surprisal_faceted.jpg\n")
  } else {
    cat("No positional summary data – skipping faceted plot.\n")
  }
}

##### Forest-style summary data #####

forest_data <- all_regressions %>%
  group_by(metric) %>%
  arrange(slope) %>%
  mutate(rank = row_number()) %>%
  ungroup()

write_csv(forest_data,
          "outputs/regression_forest_data.csv")

direction_summary <- all_regressions %>%
  mutate(
    direction = case_when(
      slope > 0 ~ "Positive",
      slope < 0 ~ "Negative",
      TRUE ~ "Zero"
    ),
    significant = p_value < .05
  ) %>%
  group_by(metric, direction) %>%
  summarise(
    n = n(),
    significant = sum(significant),
    .groups = "drop"
  )

write_csv(direction_summary,
          "outputs/regression_direction_summary.csv")

cat("\n====================================\n")
cat("All analyses complete.\n")


##### Faceted positional surprisal — high-quality greyscale, no legend #####
if (exists("all_positional") && nrow(all_positional) > 0) {
  all_positional$position <- as.numeric(all_positional$position)

  # Greyscale palette: one shade per phoneme length (3–8)
  grey_shades <- c(
    "3" = "#000000",  # black
    "4" = "#333333",
    "5" = "#666666",
    "6" = "#999999",
    "7" = "#BBBBBB",
    "8" = "#DDDDDD"
  )

  faceted <- ggplot(
    all_positional,
    aes(x = position, y = mean,
        colour = factor(n_phon),
        fill   = factor(n_phon),
        group  = factor(n_phon))
  ) +
    geom_ribbon(aes(ymin = ci_lower, ymax = ci_upper),
                alpha = 0.20, colour = NA) +
    geom_line(size = 1.1) +
    scale_colour_manual(values = grey_shades, guide = "none") +
    scale_fill_manual(values   = grey_shades, guide = "none") +
    facet_wrap(~ full_language, scales = "free_y", ncol = 5) +
    labs(x = "Bigram Position", y = "Mean Surprisal (bits)") +
    theme_minimal(base_size = 11) +
    theme(
      legend.position  = "none",
      panel.grid.minor = element_blank(),
      strip.text       = element_text(size = 10, face = "bold"),
      axis.title       = element_text(size = 11),
      axis.text        = element_text(size = 9, colour = "black"),
      panel.border     = element_rect(colour = "grey70", fill = NA, linewidth = 0.3)
    )

  ggsave(
    filename = "outputs/positional_surprisal_faceted.jpg",
    plot     = faceted,
    width    = 18,
    height   = 14,
    units    = "in",
    dpi      = 600,          # very high resolution
    device   = "jpeg",
    quality  = 100           # maximum JPEG quality
  )
  cat("Saved high-quality greyscale faceted plot to outputs/positional_surprisal_faceted.jpg\n")
} else {
  cat("No positional summary data – skipping faceted plot.\n")
}
getwd()
file.path(getwd(), "outputs", "positional_surprisal_faceted.jpg")
file.exists(file.path(getwd(), "outputs", "positional_surprisal_faceted.jpg"))
