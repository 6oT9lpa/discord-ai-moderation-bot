<script setup lang="ts">
import { computed, ref } from "vue";
import { useActivityStore } from "../../stores/activity.store";
import StatCard from "./StatCard.vue";

const activity = useActivityStore();
const userSearch = ref("");
const dailyStats = computed(() => activity.serverStats?.daily?.slice(-30) || []);
const maxDaily = computed(() => Math.max(1, ...dailyStats.value.map((row) => row.count)));
const summaryCards = computed(() => {
  const summary = activity.serverStats?.summary || {};
  return [
    ["total_messages", "Total messages"],
    ["active_users", "Active users"],
    ["active_channels", "Active channels"],
    ["voice_total_voice_minutes", "Voice minutes"],
    ["voice_voice_users", "Voice users"],
    ["joins", "Joins"],
    ["leaves", "Leaves"],
    ["period_days", "Period days"],
  ].map(([key, label]) => ({
    key,
    label,
    value: formatRecordValue(summary[key]),
    delta: key === "period_days" ? "selected range" : "tracked activity",
    tone: "neutral" as const,
  }));
});

async function searchStatsUsers() {
  await activity.searchStatsUsers(userSearch.value);
}

function formatRecordValue(value: unknown) {
  if (value === null || value === undefined || value === "") return "-";
  if (typeof value === "object") return JSON.stringify(value);
  return String(value);
}

function nestedValue(row: Record<string, unknown>, key: string, nestedKey: string) {
  const nested = row[key];
  if (!nested || typeof nested !== "object") return "-";
  return formatRecordValue((nested as Record<string, unknown>)[nestedKey]);
}
</script>

<template>
  <section class="panel-section stats-summary-panel">
    <div class="section-heading">
      <span>Server stats</span>
      <h2>Messages, channels and user activity.</h2>
      <div>
        <p>Review message volume, active members, voice time and channel trends for the selected period.</p>
      </div>
    </div>
    <div class="stats-grid">
      <StatCard
        v-for="metric in summaryCards"
        :key="metric.key"
        :metric="metric"
      />
    </div>
  </section>

  <section class="panel-section stats-chart-panel">
    <div class="section-heading">
      <span>30 day chart</span>
      <h2>Message activity by day.</h2>
    </div>
    <div class="stats-daily">
      <div v-for="point in dailyStats" :key="point.date" class="stats-day">
        <span :style="{ height: `${Math.max(4, (point.count / maxDaily) * 100)}%` }"></span>
        <small>{{ point.date.slice(5) }}</small>
      </div>
    </div>
  </section>

  <section class="panel-section stats-search-panel">
    <form class="module-toolbar" @submit.prevent="searchStatsUsers">
      <input v-model="userSearch" placeholder="Search Discord user" />
      <button class="primary-button" type="submit">Search</button>
    </form>
    <div class="record-list">
      <article v-for="row in activity.userStatsResults" :key="nestedValue(row, 'member', 'id')">
        <strong>{{ nestedValue(row, 'member', 'display_name') }}</strong>
        <span>{{ formatRecordValue(row.stats) }}</span>
      </article>
    </div>
  </section>

  <section class="panel-section stats-channel-panel">
    <div class="section-heading">
      <span>Channels</span>
      <h2>Top message channels.</h2>
    </div>
    <div class="record-list compact-list channel-stat-list">
      <article v-for="channel in (activity.serverStats?.channels || [])" :key="String(channel.channel_id)">
        <strong>#{{ channel.channel_name }}</strong>
        <span>{{ formatRecordValue(channel.messages) }} messages</span>
      </article>
    </div>
  </section>
</template>
