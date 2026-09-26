<template>
  <li>
    <div class="og-card" :class="{ 'og-root': node.isRoot }">
      <div class="og-name">{{ node.name }}</div>
      <div v-if="node.puesto" class="og-puesto">{{ node.puesto }}</div>
    </div>
    <ul v-if="node.children && node.children.length">
      <OrgNode v-for="c in node.children" :key="c.id" :node="c" />
    </ul>
  </li>
</template>

<script setup>
defineProps({ node: { type: Object, required: true } })
</script>

<style scoped>
ul {
  display: flex;
  justify-content: center;
  padding-top: 20px;
  position: relative;
  margin: 0;
  list-style: none;
}
ul::before {
  content: '';
  position: absolute;
  top: 0;
  left: 50%;
  border-left: 1px solid #cbd5e1;
  height: 20px;
}
li {
  position: relative;
  padding: 20px 10px 0;
  display: flex;
  flex-direction: column;
  align-items: center;
}
li::before,
li::after {
  content: '';
  position: absolute;
  top: 0;
  right: 50%;
  width: 50%;
  height: 20px;
  border-top: 1px solid #cbd5e1;
}
li::after {
  right: auto;
  left: 50%;
  border-left: 1px solid #cbd5e1;
}
li:only-child {
  padding-top: 0;
}
li:only-child::before,
li:only-child::after {
  display: none;
}
li:first-child::before,
li:last-child::after {
  border: 0 none;
}
li:last-child::before {
  border-right: 1px solid #cbd5e1;
}
.og-card {
  min-width: 8rem;
  max-width: 11rem;
  border: 1px solid #cbd5e1;
  border-radius: 0.5rem;
  background: #ffffff;
  padding: 0.4rem 0.6rem;
  text-align: center;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.06);
}
.og-root {
  background: #eff6ff;
  border-color: #93c5fd;
}
.og-name {
  font-size: 0.8rem;
  font-weight: 600;
  color: #1f2937;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.og-puesto {
  font-size: 0.7rem;
  color: #6b7280;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>
