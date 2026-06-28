<script setup lang="ts">
import { computed } from "vue";
import { useActivityStore } from "../../stores/activity.store";

const activity = useActivityStore();
const integrationRows = computed(() =>
  Object.entries(activity.integrations || {}).map(([key, value]) => ({
    key,
    title: key.replaceAll("_", " ").replace(/\b\w/g, (letter) => letter.toUpperCase()),
    status: integrationStatus(value),
    details: integrationDetails(value),
  })),
);

function integrationStatus(value: unknown) {
  if (Array.isArray(value)) return value.length ? `${value.length} sources` : "No sources";
  if (value && typeof value === "object") {
    return String((value as Record<string, unknown>).status || "configured");
  }
  return formatRecordValue(value);
}

function integrationDetails(value: unknown) {
  if (Array.isArray(value)) {
    if (!value.length) return "No creator platforms are connected yet.";
    return value
      .map((row) => {
        const item = row as Record<string, unknown>;
        return `${item.platform}: ${item.active_count || 0}/${item.count || 0} active`;
      })
      .join(", ");
  }
  if (value && typeof value === "object") {
    return Object.entries(value as Record<string, unknown>)
      .map(([key, item]) => `${key}: ${formatRecordValue(item)}`)
      .join(", ");
  }
  return formatRecordValue(value);
}

function formatRecordValue(value: unknown) {
  if (value === null || value === undefined || value === "") return "-";
  if (typeof value === "object") return JSON.stringify(value);
  return String(value);
}
</script>

<template>
  <section class="panel-section">
    <div class="section-heading">
      <span>Integrations</span>
      <h2>External services and connected creator platforms.</h2>
      <div>
        <p>Check Discord, creator platform, database and bot service connectivity at a glance.</p>
      </div>
    </div>
    <div class="integration-grid">
      <article v-for="row in integrationRows" :key="row.key" class="integration-card">
        <span class="status-badge success">{{ row.status }}</span>
        <strong>{{ row.title }}</strong>
        <p>{{ row.details }}</p>
      </article>
    </div>
  </section>
</template>
