<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useActivityStore } from "../../stores/activity.store";

const activity = useActivityStore();
const logQuery = ref("");
const actorQuery = ref("");
const dateFrom = ref("");
const dateTo = ref("");
const source = ref("all");
const page = ref(0);
const pageSize = 20;
const totalPages = computed(() => Math.max(1, Math.ceil((activity.auditPage?.total ?? 0) / pageSize)));
const sourceOptions = [
  { value: "all", label: "All logs" },
  { value: "moderator", label: "Log moderator" },
  { value: "welcome", label: "Log welcome" },
  { value: "messages", label: "Log message" },
  { value: "channel", label: "Log channel" },
  { value: "activity", label: "Activity changes" },
];
const combinedRows = computed(() => [
  ...(activity.logs?.audit || []).map((row) => ({ ...row, source: "audit" })),
  ...(activity.logs?.messages || []).map((row) => ({ ...row, source: "message" })),
]);

async function loadAudit() {
  await activity.loadLogs(source.value, "", logQuery.value);
  await activity.loadAuditPage({
    q: logQuery.value,
    actor: actorQuery.value,
    date_from: dateFrom.value,
    date_to: dateTo.value,
    limit: pageSize,
    offset: page.value * pageSize,
  });
}

async function applyFilters() {
  page.value = 0;
  await loadAudit();
}

async function goPage(delta: number) {
  page.value = Math.min(Math.max(page.value + delta, 0), totalPages.value - 1);
  await loadAudit();
}

function eventTitle(value: unknown) {
  const raw = String(value || "log_event");
  const named: Record<string, string> = {
    voice_join: "Voice join",
    voice_leave: "Voice leave",
    voice_move: "Voice move",
    activity_synced_role_assignments_updated: "Activity role assignments updated",
    activity_welcome_test_sent: "Welcome test sent",
  };
  return named[raw] || raw.replaceAll("_", " ").replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function actorLabel(row: Record<string, unknown>) {
  return String(row.actor_name || row.author_name || row.actor_id || row.author_id || "system");
}

function rowDetails(row: Record<string, unknown>) {
  // Convert stored bot payloads into short human-readable activity sentences.
  const eventType = String(row.event_type || "");
  const details = parseDetails(row.details ?? row.content);
  if (eventType === "voice_join" && details.channel) return `Joined voice channel ${details.channel}.`;
  if (eventType === "voice_leave" && details.channel) return `Left voice channel ${details.channel}.`;
  if (eventType === "voice_move") {
    const before = details.before_channel || "unknown";
    const after = details.after_channel || "unknown";
    return `Moved from ${before} to ${after}.`;
  }
  if (typeof details._raw === "string" && details._raw.trim()) return details._raw;
  return "No details recorded.";
}

function parseDetails(value: unknown): Record<string, unknown> & { _raw?: string } {
  if (value && typeof value === "object") return value as Record<string, unknown>;
  const raw = String(value ?? "");
  if (!raw.trim()) return {};
  try {
    return JSON.parse(raw.replaceAll("'", "\""));
  } catch {
    return { _raw: raw };
  }
}

function timeLabel(value: unknown) {
  const raw = String(value || "");
  if (!raw) return "recent";
  const parsed = new Date(raw);
  if (Number.isNaN(parsed.getTime())) return raw;
  return parsed.toLocaleString();
}

onMounted(() => {
  void loadAudit();
});
</script>

<template>
  <section class="panel-section">
    <div class="section-heading">
      <span>Logs</span>
      <h2>Searchable server and Activity logs.</h2>
      <div>
        <p>Filter bot log channels and Activity changes by source, event, date and actor.</p>
      </div>
    </div>
    <form class="module-toolbar" @submit.prevent="applyFilters">
      <input v-model="logQuery" placeholder="Search event or details" />
      <select v-model="actorQuery">
        <option value="">All users</option>
        <option v-for="actor in activity.logActors" :key="actor.id" :value="actor.id">
          {{ actor.name }} ({{ actor.id }})
        </option>
      </select>
      <select v-model="source">
        <option v-for="option in sourceOptions" :key="option.value" :value="option.value">{{ option.label }}</option>
      </select>
      <input v-model="dateFrom" type="datetime-local" />
      <input v-model="dateTo" type="datetime-local" />
      <button class="primary-button" type="submit">Apply</button>
    </form>

    <div class="record-list compact-list">
      <article v-for="row in combinedRows" :key="`log-${row.source}-${row.id}`" class="log-record">
        <strong>{{ eventTitle(row.event_type) }}</strong>
        <span>{{ actorLabel(row) }}</span>
        <p>{{ rowDetails(row) }}</p>
        <small>{{ timeLabel(row.created_at) }}</small>
      </article>
    </div>

    <div class="record-list">
      <article v-for="row in activity.auditPage?.items || []" :key="`audit-${row.id}`" class="log-record">
        <strong>{{ eventTitle(row.event_type) }}</strong>
        <span>{{ actorLabel(row as unknown as Record<string, unknown>) }}</span>
        <p>{{ rowDetails(row as unknown as Record<string, unknown>) }}</p>
        <small>{{ timeLabel(row.created_at) }}</small>
      </article>
    </div>
    <div class="pagination-row">
      <button class="ghost-button compact" type="button" :disabled="page === 0" @click="goPage(-1)">Previous</button>
      <span>{{ page + 1 }} / {{ totalPages }}</span>
      <button class="ghost-button compact" type="button" :disabled="page + 1 >= totalPages" @click="goPage(1)">Next</button>
    </div>
  </section>
</template>
