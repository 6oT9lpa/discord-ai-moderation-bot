<script setup lang="ts">
import { reactive } from "vue";
import { useActivityStore } from "../../stores/activity.store";
import type { VoiceRoom } from "../../types/activity.types";

const activity = useActivityStore();
const roomDrafts = reactive<Record<string, { name: string; userLimit: number; ownerId: string; targetUserId: string; region: string }>>({});

function draftFor(room: VoiceRoom) {
  if (!roomDrafts[room.channel_id]) {
    roomDrafts[room.channel_id] = {
      name: room.discord?.name || room.name,
      userLimit: room.discord?.user_limit ?? 0,
      ownerId: room.owner_id,
      targetUserId: "",
      region: room.discord?.rtc_region || "",
    };
  }
  return roomDrafts[room.channel_id];
}

function isLocked(room: VoiceRoom) {
  return Boolean(
    room.discord?.permission_overwrites?.some((overwrite) => {
      const item = overwrite as Record<string, unknown>;
      return item.id === String(room.guild_id) && Boolean(Number(item.deny || 0) & 0x00100000);
    }),
  );
}

async function updateRoomName(room: VoiceRoom) {
  await activity.updateVoice(room.channel_id, { name: draftFor(room).name });
}

async function updateRoomLimit(room: VoiceRoom) {
  await activity.updateVoice(room.channel_id, { user_limit: Number(draftFor(room).userLimit) });
}

async function updateRoomRegion(room: VoiceRoom) {
  await activity.updateVoice(room.channel_id, { rtc_region: draftFor(room).region || null });
}

async function transferRoom(room: VoiceRoom) {
  const ownerId = draftFor(room).ownerId.trim();
  if (!ownerId) return;
  await activity.updateVoice(room.channel_id, { owner_id: ownerId });
}

async function memberAction(room: VoiceRoom, key: "invite_user_id" | "kick_user_id" | "ban_user_id") {
  const targetUserId = draftFor(room).targetUserId.trim();
  if (!targetUserId) return;
  await activity.updateVoice(room.channel_id, { [key]: targetUserId });
}
</script>

<template>
  <section class="panel-section">
    <div class="section-heading">
      <span>Dynamic voice</span>
      <h2>Bot-created rooms and controls.</h2>
      <div>
        <p>Manage room name, limit, lock state, ownership and member access from the Activity panel.</p>
      </div>
    </div>

    <div class="voice-room-grid">
      <article v-for="room in activity.voiceRooms" :key="room.channel_id" class="voice-room-card">
        <div class="voice-room-head">
          <div>
            <strong>{{ room.discord?.name || room.name }}</strong>
            <span>Owner {{ room.owner_id }} - {{ room.is_persistent ? "persistent" : "temporary" }}</span>
          </div>
          <span :class="['status-badge', isLocked(room) ? 'warning' : 'success']">
            {{ isLocked(room) ? "locked" : "open" }}
          </span>
        </div>

        <div class="voice-control-grid">
          <label>
            Name
            <input v-model="draftFor(room).name" maxlength="100" @change="updateRoomName(room)" />
          </label>
          <label>
            Limit
            <input v-model.number="draftFor(room).userLimit" type="number" min="0" max="99" @change="updateRoomLimit(room)" />
          </label>
          <label>
            Owner ID
            <input v-model="draftFor(room).ownerId" maxlength="20" @change="transferRoom(room)" />
          </label>
          <label>
            Region
            <select v-model="draftFor(room).region" @change="updateRoomRegion(room)">
              <option value="">Automatic</option>
              <option value="europe">Europe</option>
              <option value="rotterdam">Rotterdam</option>
              <option value="us-east">US East</option>
              <option value="us-west">US West</option>
              <option value="singapore">Singapore</option>
              <option value="japan">Japan</option>
            </select>
          </label>
        </div>

        <div class="inline-actions">
          <button class="ghost-button compact" type="button" @click="activity.updateVoice(room.channel_id, { locked: true })">Lock</button>
          <button class="ghost-button compact" type="button" @click="activity.updateVoice(room.channel_id, { locked: false })">Unlock</button>
          <button class="ghost-button compact" type="button" @click="activity.updateVoice(room.channel_id, { persistent: !room.is_persistent })">
            {{ room.is_persistent ? "Temporary" : "Persist" }}
          </button>
          <button class="ghost-button danger compact" type="button" @click="activity.deleteVoice(room.channel_id)">Delete</button>
        </div>

        <div class="voice-member-actions">
          <input v-model="draftFor(room).targetUserId" maxlength="20" placeholder="Target user ID" />
          <button class="ghost-button compact" type="button" @click="memberAction(room, 'invite_user_id')">Invite</button>
          <button class="ghost-button compact" type="button" @click="memberAction(room, 'kick_user_id')">Kick</button>
          <button class="ghost-button danger compact" type="button" @click="memberAction(room, 'ban_user_id')">Ban</button>
        </div>
      </article>
    </div>
  </section>
</template>
