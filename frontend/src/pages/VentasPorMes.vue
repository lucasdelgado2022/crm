<template>
  <LayoutHeader v-if="!embedded">
    <template #left-header>
      <div class="flex items-center gap-2 text-lg font-semibold text-ink-gray-8">
        <ChartIcon class="h-5 w-5" />
        {{ __('Ventas por Mes') }}
      </div>
    </template>
    <template #right-header>
      <div class="flex items-center gap-3">
        <!-- Solo ganadas -->
        <label
          class="flex cursor-pointer items-center gap-1.5 text-sm text-ink-gray-7"
        >
          <input v-model="onlyWon" type="checkbox" class="rounded" />
          {{ __('Solo ganadas') }}
        </label>
        <!-- Incluir sin fecha de cierre -->
        <label
          class="flex cursor-pointer items-center gap-1.5 text-sm text-ink-gray-7"
        >
          <input v-model="includeNoDate" type="checkbox" class="rounded" />
          {{ __('Sin fecha') }}
        </label>
        <!-- Tipo: venta / renovación -->
        <select
          v-model="tipoFilter"
          class="h-8 rounded-lg border border-outline-gray-2 bg-surface-base px-2 text-sm text-ink-gray-8 focus:outline-none"
        >
          <option value="">{{ __('Todos los tipos') }}</option>
          <option value="venta">{{ __('Solo Venta') }}</option>
          <option value="renovacion">{{ __('Solo Renovación') }}</option>
          <option value="servicio">{{ __('Solo Servicio') }}</option>
        </select>
        <select
          v-model="canalFilter"
          class="h-8 rounded-lg border border-outline-gray-2 bg-surface-base px-2 text-sm text-ink-gray-8 focus:outline-none"
        >
          <option value="">{{ __('Todos los canales') }}</option>
          <option v-for="c in CANALES" :key="c" :value="c">{{ c }}</option>
        </select>
        <select
          v-model="respFilter"
          class="h-8 rounded-lg border border-outline-gray-2 bg-surface-base px-2 text-sm text-ink-gray-8 focus:outline-none"
        >
          <option value="">{{ __('Todos los responsables') }}</option>
          <option v-for="o in owners" :key="o.value" :value="o.value">
            {{ o.label }}
          </option>
        </select>
        <select
          v-model="productFilter"
          class="h-8 rounded-lg border border-outline-gray-2 bg-surface-base px-2 text-sm text-ink-gray-8 focus:outline-none"
        >
          <option value="">{{ __('Todos los productos') }}</option>
          <option v-for="p in productos" :key="p" :value="p">{{ p }}</option>
        </select>
        <!-- Año -->
        <select
          v-model.number="year"
          class="h-8 rounded-lg border border-outline-gray-2 bg-surface-base px-2 text-sm text-ink-gray-8 focus:outline-none"
        >
          <option v-for="y in years" :key="y" :value="y">{{ y }}</option>
        </select>
      </div>
    </template>
  </LayoutHeader>

  <div class="flex h-full flex-col overflow-y-auto p-4 sm:p-6">
    <!-- Selector de monto -->
    <div class="mb-4 flex flex-wrap items-center gap-2">
      <span class="text-sm text-ink-gray-5">{{ __('Monto') }}:</span>
      <div class="flex rounded-lg border border-outline-gray-2 p-0.5">
        <button
          v-for="opt in amountOptions"
          :key="opt.key"
          class="rounded-md px-3 py-1 text-sm font-medium transition"
          :class="
            amount === opt.key
              ? 'bg-surface-gray-3 text-ink-gray-9'
              : 'text-ink-gray-6 hover:text-ink-gray-9'
          "
          @click="amount = opt.key"
        >
          {{ opt.label }}
        </button>
      </div>
      <!-- Controles año/solo-ganadas cuando está embebido en Dashboard -->
      <template v-if="embedded">
        <label
          class="ml-auto flex cursor-pointer items-center gap-1.5 text-sm text-ink-gray-7"
        >
          <input v-model="onlyWon" type="checkbox" class="rounded" />
          {{ __('Solo ganadas') }}
        </label>
        <label
          class="flex cursor-pointer items-center gap-1.5 text-sm text-ink-gray-7"
        >
          <input v-model="includeNoDate" type="checkbox" class="rounded" />
          {{ __('Sin fecha') }}
        </label>
        <select
          v-model="tipoFilter"
          class="h-8 rounded-lg border border-outline-gray-2 bg-surface-base px-2 text-sm text-ink-gray-8 focus:outline-none"
        >
          <option value="">{{ __('Todos los tipos') }}</option>
          <option value="venta">{{ __('Solo Venta') }}</option>
          <option value="renovacion">{{ __('Solo Renovación') }}</option>
          <option value="servicio">{{ __('Solo Servicio') }}</option>
        </select>
        <select
          v-model="canalFilter"
          class="h-8 rounded-lg border border-outline-gray-2 bg-surface-base px-2 text-sm text-ink-gray-8 focus:outline-none"
        >
          <option value="">{{ __('Todos los canales') }}</option>
          <option v-for="c in CANALES" :key="c" :value="c">{{ c }}</option>
        </select>
        <select
          v-model="respFilter"
          class="h-8 rounded-lg border border-outline-gray-2 bg-surface-base px-2 text-sm text-ink-gray-8 focus:outline-none"
        >
          <option value="">{{ __('Todos los responsables') }}</option>
          <option v-for="o in owners" :key="o.value" :value="o.value">
            {{ o.label }}
          </option>
        </select>
        <select
          v-model="productFilter"
          class="h-8 rounded-lg border border-outline-gray-2 bg-surface-base px-2 text-sm text-ink-gray-8 focus:outline-none"
        >
          <option value="">{{ __('Todos los productos') }}</option>
          <option v-for="p in productos" :key="p" :value="p">{{ p }}</option>
        </select>
        <select
          v-model.number="year"
          class="h-8 rounded-lg border border-outline-gray-2 bg-surface-base px-2 text-sm text-ink-gray-8 focus:outline-none"
        >
          <option v-for="y in years" :key="y" :value="y">{{ y }}</option>
        </select>
      </template>
    </div>

    <!-- KPIs anuales de cierre (Dashboard Comercial) -->
    <div class="mb-5 grid grid-cols-2 gap-3 sm:grid-cols-5">
      <div class="rounded-lg border border-green-200 bg-green-50/40 p-3">
        <div class="text-xs font-medium text-green-700">{{ __('Cerrado') }} {{ year }}</div>
        <div class="mt-0.5 text-xl font-semibold text-green-700">{{ money(kpi.wonAmt) }}</div>
        <div class="text-xs text-ink-gray-5">{{ kpi.wonCnt }} {{ __('ventas') }}</div>
      </div>
      <div class="rounded-lg border border-violet-200 bg-violet-50/40 p-3">
        <div class="text-xs font-medium text-violet-700">{{ __('Pipeline') }} {{ year }}</div>
        <div class="mt-0.5 text-xl font-semibold text-violet-700">{{ money(kpi.openAmt) }}</div>
        <div class="text-xs text-ink-gray-5">{{ kpi.openCnt }} {{ __('oportunidades') }}</div>
      </div>
      <div class="rounded-lg border p-3">
        <div class="text-xs text-ink-gray-5">{{ __('Ticket promedio') }}</div>
        <div class="mt-0.5 text-xl font-semibold text-ink-gray-9">{{ money(kpi.ticket) }}</div>
        <div class="text-xs text-ink-gray-5">{{ __('por venta') }}</div>
      </div>
      <div class="rounded-lg border p-3">
        <div class="text-xs text-ink-gray-5">{{ __('Win rate') }}</div>
        <div class="mt-0.5 text-xl font-semibold text-ink-gray-9">{{ kpi.winRate }}%</div>
        <div class="text-xs text-ink-gray-5">{{ kpi.wonCnt }} / {{ kpi.wonCnt + kpi.lostCnt }} {{ __('cerradas') }}</div>
      </div>
      <div class="rounded-lg border p-3">
        <div class="text-xs text-ink-gray-5">{{ __('Perdido') }} {{ year }}</div>
        <div class="mt-0.5 text-xl font-semibold text-red-700">{{ money(kpi.lostAmt) }}</div>
        <div class="text-xs text-ink-gray-5">{{ kpi.lostCnt }} {{ __('oportunidades') }}</div>
      </div>
    </div>

    <!-- Gráfico de barras -->
    <div class="rounded-lg border p-4">
      <div class="mb-3 flex flex-wrap items-center gap-x-4 gap-y-2 text-xs text-ink-gray-6">
        <template v-if="chartMode === 'estado'">
          <span class="flex items-center gap-1.5">
            <span class="h-2.5 w-2.5 rounded-sm bg-green-500" />
            {{ __('Ganadas') }}
          </span>
          <span class="flex items-center gap-1.5">
            <span class="h-2.5 w-2.5 rounded-sm bg-violet-500" />
            {{ __('Proyectadas') }}
          </span>
        </template>
        <template v-else-if="chartMode === 'responsable'">
          <span v-for="o in chartOwners" :key="o" class="flex items-center gap-1.5">
            <span class="h-2.5 w-2.5 rounded-sm" :class="ownerColor(o)" />
            {{ userMap[o] || o }}
          </span>
        </template>
        <template v-else-if="chartMode === 'pais'">
          <span v-for="c in chartCountries" :key="c" class="flex items-center gap-1.5">
            <span class="h-2.5 w-2.5 rounded-sm" :style="{ backgroundColor: countryColorHex(c) }" />
            {{ c }}
          </span>
        </template>
        <div class="ml-auto flex flex-wrap items-center gap-2">
          <button
            class="flex items-center gap-1.5 rounded-lg border border-outline-gray-2 px-3 py-1 text-xs font-medium hover:bg-surface-gray-2"
            :class="groupBy === 'quarter' ? 'bg-surface-gray-3 text-ink-gray-9' : 'text-ink-gray-7'"
            @click="groupBy = groupBy === 'quarter' ? 'mes' : 'quarter'"
          >
            {{ __('Totales por quarter') }}
          </button>
          <button
            class="flex items-center gap-1.5 rounded-lg border border-outline-gray-2 px-3 py-1 text-xs font-medium hover:bg-surface-gray-2"
            :class="groupBy === 'anio' ? 'bg-surface-gray-3 text-ink-gray-9' : 'text-ink-gray-7'"
            @click="groupBy = groupBy === 'anio' ? 'mes' : 'anio'"
          >
            {{ __('Totales por año') }}
          </button>
          <button
            class="flex items-center gap-1.5 rounded-lg border border-outline-gray-2 px-3 py-1 text-xs font-medium hover:bg-surface-gray-2"
            :class="chartMode === 'responsable' ? 'bg-surface-gray-3 text-ink-gray-9' : 'text-ink-gray-7'"
            @click="chartMode = chartMode === 'responsable' ? 'estado' : 'responsable'"
          >
            <UsersIcon class="h-3.5 w-3.5" />
            {{ __('Por responsable') }}
          </button>
          <button
            class="flex items-center gap-1.5 rounded-lg border border-outline-gray-2 px-3 py-1 text-xs font-medium hover:bg-surface-gray-2"
            :class="chartMode === 'pais' ? 'bg-surface-gray-3 text-ink-gray-9' : 'text-ink-gray-7'"
            @click="chartMode = chartMode === 'pais' ? 'estado' : 'pais'"
          >
            {{ __('Comparar por país') }}
          </button>
        </div>
      </div>
      <div
        v-if="loading"
        class="flex h-64 items-center justify-center text-ink-gray-4"
      >
        {{ __('Cargando...') }}
      </div>
      <div
        v-else-if="!yearTotal"
        class="flex h-64 flex-col items-center justify-center gap-2 text-ink-gray-4"
      >
        <ChartIcon class="h-8 w-8" />
        <span>{{ __('Sin datos para') }} {{ year }}</span>
      </div>
      <div
        v-else-if="chartMode === 'estado'"
        class="flex h-72 items-end gap-2 sm:gap-3"
      >
        <div
          v-for="(m, i) in chartBuckets"
          :key="i"
          class="group flex h-full flex-1 flex-col items-center justify-end"
          :class="groupBy === 'mes' ? 'cursor-pointer' : ''"
          @click="groupBy === 'mes' ? selectBucket(i) : null"
        >
          <div
            class="mb-1 whitespace-nowrap text-[10px] font-semibold text-ink-gray-7 sm:text-xs"
          >
            {{ m.count ? moneyShort(m.total) + ' (' + m.count + ')' : '' }}
          </div>
          <div
            class="w-full overflow-hidden rounded-t transition-all"
            :class="groupBy === 'mes' && selected === i ? 'ring-2 ring-ink-gray-4' : ''"
            :style="{ height: bucketBarHeight(m.total) }"
            :title="
              m.label +
              ': ' +
              money(m.total) +
              ' — Ganadas ' +
              money(m.wonAmt) +
              ' / Proyectadas ' +
              money(m.projAmt)
            "
          >
            <div class="w-full bg-violet-500" :style="{ height: segPct(m.projNuevaAmt, m.total) + '%' }" />
            <div class="w-full bg-violet-300" :style="{ height: segPct(m.projRenovAmt, m.total) + '%' }" />
            <div class="w-full bg-green-500" :style="{ height: segPct(m.wonNuevaAmt, m.total) + '%' }" />
            <div class="w-full bg-green-300" :style="{ height: segPct(m.wonRenovAmt, m.total) + '%' }" />
          </div>
          <div
            class="mt-1.5 text-xs"
            :class="groupBy === 'mes' && selected === i ? 'font-semibold text-ink-gray-8' : 'text-ink-gray-5'"
          >
            {{ m.label }}
          </div>
        </div>
        <!-- Barra: oportunidades sin fecha de cierre -->
        <div
          v-if="groupBy === 'mes' && showNoDate"
          class="group flex h-full flex-1 cursor-pointer flex-col items-center justify-end"
          @click="selectBucket('nodate')"
        >
          <div
            class="mb-1 whitespace-nowrap text-[10px] font-semibold text-ink-gray-7 sm:text-xs"
          >
            {{ noDate.count ? moneyShort(noDate.total) + ' (' + noDate.count + ')' : '' }}
          </div>
          <div
            class="w-full overflow-hidden rounded-t transition-all"
            :class="selected === 'nodate' ? 'ring-2 ring-ink-gray-4' : ''"
            :style="{ height: barHeight(noDate.total) }"
            :title="
              'Sin fecha: ' +
              money(noDate.total) +
              ' — Ganadas ' +
              money(noDate.wonAmt) +
              ' / Proyectadas ' +
              money(noDate.projAmt)
            "
          >
            <div class="w-full bg-violet-500" :style="{ height: segPct(noDate.projNuevaAmt, noDate.total) + '%' }" />
            <div class="w-full bg-violet-300" :style="{ height: segPct(noDate.projRenovAmt, noDate.total) + '%' }" />
            <div class="w-full bg-green-500" :style="{ height: segPct(noDate.wonNuevaAmt, noDate.total) + '%' }" />
            <div class="w-full bg-green-300" :style="{ height: segPct(noDate.wonRenovAmt, noDate.total) + '%' }" />
          </div>
          <div
            class="mt-1.5 text-xs"
            :class="
              selected === 'nodate'
                ? 'font-semibold text-ink-gray-8'
                : 'text-ink-gray-5'
            "
          >
            {{ __('Sin fecha') }}
          </div>
        </div>
      </div>
      <!-- Barras agrupadas por responsable comercial (una barra por resp. por mes) -->
      <div v-else-if="chartMode === 'responsable'" class="flex h-72 items-end gap-2 sm:gap-3">
        <div
          v-for="(m, i) in byOwnerData.months"
          :key="i"
          class="flex h-full flex-1 flex-col items-center justify-end"
        >
          <div class="flex h-full w-full items-end justify-center gap-0.5">
            <div
              v-for="o in chartOwners"
              :key="o"
              class="flex h-full min-w-0 flex-1 flex-col items-center justify-end"
            >
              <div
                v-if="(m[o]?.amt || 0) > 0"
                class="mb-0.5 whitespace-nowrap text-[9px] font-semibold leading-tight text-ink-gray-7"
              >
                {{ moneyShort(m[o].amt) }} ({{ m[o].cnt }})
              </div>
              <div
                class="w-full rounded-t transition-all hover:opacity-80"
                :class="[ownerColor(o), (m[o]?.amt || 0) > 0 ? '' : 'opacity-0']"
                :style="{ height: ownerBarHeight(m[o]?.amt || 0) }"
                :title="(userMap[o] || o) + ' — ' + MONTHS[i] + ': ' + money(m[o]?.amt || 0) + ' (' + (m[o]?.cnt || 0) + ')'"
              />
            </div>
          </div>
          <div class="mt-1.5 text-xs text-ink-gray-5">{{ MONTHS[i] }}</div>
        </div>
      </div>
      <!-- Barras agrupadas por país del cliente (una barra por país por mes) -->
      <div v-else-if="chartMode === 'pais'" class="flex h-72 items-end gap-2 sm:gap-3">
        <div
          v-for="(m, i) in byCountryData.months"
          :key="i"
          class="flex h-full flex-1 flex-col items-center justify-end"
        >
          <div class="flex h-full w-full items-end justify-center gap-0.5">
            <div
              v-for="c in chartCountries"
              :key="c"
              class="flex h-full min-w-0 flex-1 flex-col items-center justify-end"
            >
              <div
                v-if="(m[c]?.amt || 0) > 0"
                class="mb-0.5 whitespace-nowrap text-[9px] font-semibold leading-tight text-ink-gray-7"
              >
                {{ moneyShort(m[c].amt) }} ({{ m[c].cnt }})
              </div>
              <div
                class="w-full rounded-t transition-all hover:opacity-80"
                :class="(m[c]?.amt || 0) > 0 ? '' : 'opacity-0'"
                :style="{ height: countryBarHeight(m[c]?.amt || 0), backgroundColor: countryColorHex(c) }"
                :title="c + ' — ' + MONTHS[i] + ': ' + money(m[c]?.amt || 0) + ' (' + (m[c]?.cnt || 0) + ')'"
              />
            </div>
          </div>
          <div class="mt-1.5 text-xs text-ink-gray-5">{{ MONTHS[i] }}</div>
        </div>
      </div>
    </div>

    <!-- Ranking por responsable (modo responsable) -->
    <div v-if="chartMode === 'responsable'" class="mt-5 rounded-lg border">
      <div class="border-b px-4 py-3 text-sm font-semibold text-ink-gray-8">
        {{ __('Por responsable comercial') }} · {{ year }}
      </div>
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead class="border-b bg-surface-gray-1 text-xs text-ink-gray-5">
            <tr>
              <th class="px-4 py-2 text-left">{{ __('Responsable') }}</th>
              <th class="px-4 py-2 text-right">{{ __('Ventas') }}</th>
              <th class="px-4 py-2 text-right">{{ __('Cerrado') }}</th>
              <th class="px-4 py-2 text-right">{{ __('Pipeline') }}</th>
              <th class="px-4 py-2 text-right">{{ __('Ticket prom.') }}</th>
              <th class="px-4 py-2 text-right">{{ __('Totales') }}</th>
              <th class="px-4 py-2 text-right">{{ __('Win rate') }}</th>
            </tr>
          </thead>
          <tbody class="divide-y">
            <tr v-for="r in ranking" :key="r.owner" class="hover:bg-surface-gray-1">
              <td class="px-4 py-2 text-ink-gray-9">{{ userMap[r.owner] || r.owner }}</td>
              <td class="px-4 py-2 text-right text-green-700">{{ r.wonCnt }}</td>
              <td class="px-4 py-2 text-right font-medium text-ink-gray-9">{{ money(r.wonAmt) }}</td>
              <td class="px-4 py-2 text-right text-violet-700">{{ money(r.openAmt) }}</td>
              <td class="px-4 py-2 text-right text-ink-gray-7">{{ money(r.ticket) }}</td>
              <td class="px-4 py-2 text-right font-medium text-ink-gray-9">{{ money(r.total) }}</td>
              <td class="px-4 py-2 text-right text-ink-gray-7">{{ r.winRate }}%</td>
            </tr>
            <tr v-if="!ranking.length">
              <td colspan="7" class="px-4 py-6 text-center text-ink-gray-4">{{ __('Sin datos') }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Lista de oportunidades del bucket seleccionado -->
    <div v-if="selected !== null" class="mt-5 rounded-lg border">
      <div class="flex items-center justify-between border-b px-4 py-3">
        <div class="text-sm font-semibold text-ink-gray-8">
          {{ __('Oportunidades') }}: {{ selectedLabel }}
          <span class="font-normal text-ink-gray-5"
            >({{ selectedDeals.length }})</span
          >
        </div>
        <button
          class="text-sm text-ink-gray-5 hover:text-ink-gray-8"
          @click="selected = null"
        >
          {{ __('Cerrar') }}
        </button>
      </div>
      <div v-if="selectedDeals.length" class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead class="border-b bg-surface-gray-1 text-xs text-ink-gray-5">
            <tr>
              <th class="px-4 py-2 text-left font-medium">{{ __('N° Op') }}</th>
              <th class="px-4 py-2 text-left font-medium">{{ __('Título') }}</th>
              <th class="px-4 py-2 text-left font-medium">
                {{ __('Organización') }}
              </th>
              <th class="px-4 py-2 text-left font-medium">{{ __('Producto') }}</th>
              <th class="px-4 py-2 text-left font-medium">{{ __('Responsable') }}</th>
              <th class="px-4 py-2 text-left font-medium">{{ __('Tipo') }}</th>
              <th class="px-4 py-2 text-left font-medium">{{ __('Estado') }}</th>
              <th class="px-4 py-2 text-right font-medium">{{ __('Monto') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="d in selectedDeals"
              :key="d.name"
              class="cursor-pointer border-b last:border-0 hover:bg-surface-gray-1"
              @click="openDeal(d.name)"
            >
              <td class="px-4 py-2 text-ink-gray-7">
                {{ d.custom_numero_solaer || '—' }}
              </td>
              <td class="px-4 py-2 text-ink-gray-8">
                {{ d.custom_titulo || '—' }}
              </td>
              <td class="px-4 py-2 text-ink-gray-8">
                {{ d.organization || d.name }}
              </td>
              <td class="px-4 py-2 text-ink-gray-6">
                {{ d.custom_producto || '—' }}
              </td>
              <td class="px-4 py-2 text-ink-gray-7">
                <span v-if="d.deal_owner" class="flex items-center gap-1.5">
                  <UserAvatar :user="d.deal_owner" size="sm" />
                  {{ userMap[d.deal_owner] || d.deal_owner }}
                </span>
                <span v-else>—</span>
              </td>
              <td class="px-4 py-2 text-ink-gray-6">
                {{ d.custom_tipo_oportunidad || '—' }}
              </td>
              <td class="px-4 py-2">
                <span
                  class="rounded px-1.5 py-0.5 text-xs font-medium"
                  :class="
                    d.status === 'Won'
                      ? 'bg-green-100 text-green-700'
                      : d.status === 'Lost'
                        ? 'bg-red-100 text-red-700'
                        : 'text-ink-gray-6'
                  "
                  >{{ d.status || '—' }}</span
                >
              </td>
              <td class="px-4 py-2 text-right font-medium text-ink-gray-9">
                {{ money(Number(d[amount]) || 0) }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-else class="px-4 py-6 text-center text-sm text-ink-gray-4">
        {{ __('Sin oportunidades') }}
      </div>
    </div>

    <!-- Tabla -->
    <div class="mt-5 overflow-x-auto rounded-lg border">
      <table class="w-full text-sm">
        <thead class="border-b bg-surface-gray-1 text-xs text-ink-gray-5">
          <tr>
            <th class="px-4 py-2 text-left font-medium">{{ __('Mes') }}</th>
            <th class="px-4 py-2 text-right font-medium">{{ __('Oportunidades') }}</th>
            <th class="px-4 py-2 text-right font-medium">{{ __('Ganadas') }}</th>
            <th class="px-4 py-2 text-right font-medium">{{ __('Monto') }}</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="(m, i) in monthly"
            :key="i"
            class="border-b last:border-0 hover:bg-surface-gray-1"
          >
            <td class="px-4 py-2 text-ink-gray-8">{{ MONTHS_FULL[i] }}</td>
            <td class="px-4 py-2 text-right text-ink-gray-7">{{ m.count }}</td>
            <td class="px-4 py-2 text-right text-green-700">{{ m.won }}</td>
            <td class="px-4 py-2 text-right font-medium text-ink-gray-9">
              {{ m.total ? money(m.total) : '—' }}
            </td>
          </tr>
          <tr
            v-if="showNoDate"
            class="border-b last:border-0 hover:bg-surface-gray-1"
          >
            <td class="px-4 py-2 text-ink-gray-8">
              {{ __('Sin fecha de cierre') }}
            </td>
            <td class="px-4 py-2 text-right text-ink-gray-7">
              {{ noDate.count }}
            </td>
            <td class="px-4 py-2 text-right text-green-700">{{ noDate.won }}</td>
            <td class="px-4 py-2 text-right font-medium text-ink-gray-9">
              {{ noDate.total ? money(noDate.total) : '—' }}
            </td>
          </tr>
        </tbody>
        <tfoot>
          <tr class="border-t bg-surface-gray-1 font-semibold">
            <td class="px-4 py-2 text-ink-gray-9">{{ __('Total') }}</td>
            <td class="px-4 py-2 text-right text-ink-gray-9">{{ yearCount }}</td>
            <td class="px-4 py-2 text-right text-green-700">{{ yearWon }}</td>
            <td class="px-4 py-2 text-right text-ink-gray-9">{{ money(yearTotal) }}</td>
          </tr>
        </tfoot>
      </table>
    </div>
  </div>
</template>

<script setup>
import LayoutHeader from '@/components/LayoutHeader.vue'
import UserAvatar from '@/components/UserAvatar.vue'
import ChartIcon from '~icons/lucide/bar-chart-3'
import UsersIcon from '~icons/lucide/users'
import { createResource } from 'frappe-ui'
import { sessionStore } from '@/stores/session'
import { usersStore } from '@/stores/users'
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

defineProps({
  embedded: { type: Boolean, default: false },
})

const MONTHS = ['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic']
const MONTHS_FULL = ['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre']

const amountOptions = [
  { key: 'custom_solaer_revenue', label: 'Solaer Revenue' },
  { key: 'custom_ds_revenue', label: 'DS Revenue' },
  { key: 'deal_value', label: 'Valor de Oportunidad' },
]
const amount = ref('custom_solaer_revenue')
const onlyWon = ref(false)
const year = ref(new Date().getFullYear())
// '' = todos, 'venta' = Nuevo:*, 'renovacion' = Renovación:*
const CANALES = ['CPE', 'CRE', 'CPE: GEOVIA', 'Servicios']
const tipoFilter = ref('')
const canalFilter = ref('')
// responsable comercial (deal_owner)
const respFilter = ref('')
const productFilter = ref('')
// incluir oportunidades sin fecha de cierre en un bucket "Sin fecha"
const includeNoDate = ref(true)
// modo del gráfico: 'estado' (Ganadas/Proyectadas) | 'responsable' (barra por responsable)
const chartMode = ref('estado')

// pasa los filtros de "solo ganadas" y tipo (venta/renovación)
function passesFilters(d) {
  if (onlyWon.value && d.status !== 'Won') return false
  const t = d.custom_tipo_oportunidad || ''
  if (tipoFilter.value === 'venta' && !t.startsWith('Nuevo')) return false
  if (tipoFilter.value === 'renovacion' && !t.startsWith('Renov')) return false
  if (tipoFilter.value === 'servicio' && !t.startsWith('Servicio')) return false
  if (respFilter.value && d.deal_owner !== respFilter.value) return false
  if (canalFilter.value && (d.custom_canal || '') !== canalFilter.value) return false
  if (productFilter.value && (d.custom_producto || '') !== productFilter.value) return false
  return true
}

// Fecha usada en el gráfico: para ganadas -> Closed Date (real);
// para el resto -> Expected Closure Date (proyectada).
function dealDate(d) {
  return d.closed_date || d.expected_closure_date || ''
}

const { user: sessionUser } = sessionStore()
const { isAdmin } = usersStore()
const dealsRes = createResource({
  url: 'frappe.client.get_list',
  params: {
    doctype: 'CRM Deal',
    fields: [
      'expected_closure_date',
      'closed_date',
      'status',
      'deal_value',
      'custom_ds_revenue',
      'custom_solaer_revenue',
      'custom_tipo_oportunidad',
      'custom_canal',
      'deal_owner',
      'name',
      'organization',
      'custom_producto',
      'custom_numero_solaer',
      'custom_titulo',
    ],
    limit_page_length: 0,
  },
  auto: true,
})
const deals = computed(() => {
  const all = dealsRes.data || []
  try { if (isAdmin()) return all } catch (e) {}
  return all.filter((d) => d.deal_owner === sessionUser)
})
const productos = computed(() => {
  const set = new Set()
  for (const d of deals.value) if (d.custom_producto) set.add(d.custom_producto)
  return [...set].sort((a, b) => String(a).localeCompare(String(b)))
})

// Proyectadas = solo etapas avanzadas (4 Negociación y 5 Listo para cerrar)
const PROJ_STATUSES = ['4. Negociación', '5. Listo para cerrar']
function isRenov(d) {
  return /^renovaci/i.test(d.custom_tipo_oportunidad || '')
}

// responsables (deal_owner) para el filtro, con nombre completo
const usersRes = createResource({
  url: 'frappe.client.get_list',
  params: {
    doctype: 'User',
    fields: ['name', 'full_name'],
    filters: { enabled: 1 },
    limit_page_length: 0,
  },
  auto: true,
})
const userMap = computed(() => {
  const m = {}
  for (const u of usersRes.data || []) m[u.name] = u.full_name || u.name
  return m
})
const owners = computed(() => {
  const set = new Set()
  for (const d of deals.value) if (d.deal_owner) set.add(d.deal_owner)
  return [...set]
    .map((v) => ({ value: v, label: userMap.value[v] || v }))
    .sort((a, b) => a.label.localeCompare(b.label))
})
const loading = computed(() => dealsRes.loading)

const years = computed(() => {
  const s = new Set()
  for (const d of deals.value) {
    const dt = dealDate(d)
    if (dt) s.add(Number(dt.slice(0, 4)))
  }
  s.add(new Date().getFullYear())
  return [...s].sort((a, b) => b - a)
})

// wonAmt = monto de ganadas (verde) | projAmt = monto del resto/proyectadas (violeta)
const monthly = computed(() => {
  const arr = Array.from({ length: 12 }, () => ({
    total: 0,
    count: 0,
    won: 0,
    wonAmt: 0,
    projAmt: 0,
    wonNuevaAmt: 0,
    wonRenovAmt: 0,
    projNuevaAmt: 0,
    projRenovAmt: 0,
  }))
  for (const d of deals.value) {
    const dt = dealDate(d)
    if (!dt) continue
    if (Number(dt.slice(0, 4)) !== year.value) continue
    if (!passesFilters(d)) continue
    const isWon = d.status === 'Won'
    const isProj = PROJ_STATUSES.includes(d.status)
    if (!isWon && !isProj) continue
    const mi = Number(dt.slice(5, 7)) - 1
    if (mi < 0 || mi > 11) continue
    const val = Number(d[amount.value]) || 0
    arr[mi].total += val
    arr[mi].count += 1
    if (isWon) {
      arr[mi].won += 1
      arr[mi].wonAmt += val
      if (isRenov(d)) arr[mi].wonRenovAmt += val
      else arr[mi].wonNuevaAmt += val
    } else {
      arr[mi].projAmt += val
      if (isRenov(d)) arr[mi].projRenovAmt += val
      else arr[mi].projNuevaAmt += val
    }
  }
  return arr
})

// Oportunidades SIN fecha de cierre (no caen en ningún mes/año)
const noDate = computed(() => {
  const b = { total: 0, count: 0, won: 0, wonAmt: 0, projAmt: 0, wonNuevaAmt: 0, wonRenovAmt: 0, projNuevaAmt: 0, projRenovAmt: 0 }
  if (!includeNoDate.value) return b
  for (const d of deals.value) {
    if (dealDate(d)) continue
    if (!passesFilters(d)) continue
    const isWon = d.status === 'Won'
    const isProj = PROJ_STATUSES.includes(d.status)
    if (!isWon && !isProj) continue
    const val = Number(d[amount.value]) || 0
    b.total += val
    b.count += 1
    if (isWon) {
      b.won += 1
      b.wonAmt += val
      if (isRenov(d)) b.wonRenovAmt += val
      else b.wonNuevaAmt += val
    } else {
      b.projAmt += val
      if (isRenov(d)) b.projRenovAmt += val
      else b.projNuevaAmt += val
    }
  }
  return b
})

// % de cada segmento dentro de la barra
function segPct(part, total) {
  if (!total) return 0
  return (part / total) * 100
}

// ---- Gráfico agrupado por responsable comercial ----
const OWNER_COLORS = [
  'bg-blue-500',
  'bg-green-500',
  'bg-violet-500',
  'bg-amber-500',
  'bg-rose-500',
  'bg-cyan-500',
  'bg-fuchsia-500',
  'bg-lime-500',
  'bg-orange-500',
  'bg-teal-500',
  'bg-indigo-500',
  'bg-pink-500',
]
// Por mes: monto por responsable (respeta los mismos filtros y monto que el resto)
const byOwnerData = computed(() => {
  const months = Array.from({ length: 12 }, () => ({}))
  const ownerSet = new Set()
  for (const d of deals.value) {
    const dt = dealDate(d)
    if (!dt) continue
    if (Number(dt.slice(0, 4)) !== year.value) continue
    if (!passesFilters(d)) continue
    const mi = Number(dt.slice(5, 7)) - 1
    if (mi < 0 || mi > 11) continue
    const owner = d.deal_owner || '—'
    ownerSet.add(owner)
    const cell = months[mi][owner] || (months[mi][owner] = { amt: 0, cnt: 0 })
    cell.amt += Number(d[amount.value]) || 0
    cell.cnt += 1
  }
  const list = [...ownerSet].sort((a, b) =>
    (userMap.value[a] || a).localeCompare(userMap.value[b] || b),
  )
  return { months, owners: list }
})
const chartOwners = computed(() => byOwnerData.value.owners)
function ownerColor(owner) {
  const idx = chartOwners.value.indexOf(owner)
  return OWNER_COLORS[(idx < 0 ? 0 : idx) % OWNER_COLORS.length]
}
const maxOwnerVal = computed(() => {
  let mx = 1
  for (const m of byOwnerData.value.months)
    for (const o in m) if (m[o].amt > mx) mx = m[o].amt
  return mx
})
function ownerBarHeight(v) {
  const pct = (v / maxOwnerVal.value) * 100
  return (v > 0 ? Math.max(2, pct) : 0) + '%'
}
// ---- Comparar por país del cliente ----
const orgsRes = createResource({
  url: 'frappe.client.get_list',
  params: { doctype: 'CRM Organization', fields: ['name', 'territory'], limit_page_length: 0 },
  auto: true,
})
const orgCountry = computed(() => {
  const m = {}
  for (const o of orgsRes.data || []) m[o.name] = o.territory || '—'
  return m
})
function dealCountry(d) {
  return orgCountry.value[d.organization] || '—'
}
const byCountryData = computed(() => {
  const months = Array.from({ length: 12 }, () => ({}))
  const set = new Set()
  for (const d of deals.value) {
    const dt = dealDate(d)
    if (!dt) continue
    if (Number(dt.slice(0, 4)) !== year.value) continue
    if (!passesFilters(d)) continue
    const mi = Number(dt.slice(5, 7)) - 1
    if (mi < 0 || mi > 11) continue
    const c = dealCountry(d)
    set.add(c)
    const cell = months[mi][c] || (months[mi][c] = { amt: 0, cnt: 0 })
    cell.amt += Number(d[amount.value]) || 0
    cell.cnt += 1
  }
  const list = [...set].sort((a, b) => String(a).localeCompare(String(b)))
  return { months, countries: list }
})
const chartCountries = computed(() => byCountryData.value.countries)
function countryColor(c) {
  const idx = chartCountries.value.indexOf(c)
  return OWNER_COLORS[(idx < 0 ? 0 : idx) % OWNER_COLORS.length]
}
// Colores fijos por país del cliente
const COUNTRY_FALLBACK = ['#3b82f6', '#22c55e', '#a855f7', '#f59e0b', '#06b6d4', '#ec4899', '#84cc16', '#f97316', '#14b8a6', '#6366f1']
function countryColorHex(c) {
  const k = String(c).toLowerCase()
  if (k.includes('argentin')) return '#38bdf8'
  if (k.includes('urugua')) return '#38bdf8'
  if (k.includes('chile')) return '#fca5a5'
  if (k.includes('per')) return '#b91c1c'
  if (k.includes('colombi')) return '#8b5e3c'
  const idx = chartCountries.value.indexOf(c)
  return COUNTRY_FALLBACK[(idx < 0 ? 0 : idx) % COUNTRY_FALLBACK.length]
}
const maxCountryVal = computed(() => {
  let mx = 1
  for (const m of byCountryData.value.months)
    for (const c in m) if (m[c].amt > mx) mx = m[c].amt
  return mx
})
function countryBarHeight(v) {
  const pct = (v / maxCountryVal.value) * 100
  return (v > 0 ? Math.max(2, pct) : 0) + '%'
}

// ---- Totales por quarter ----
const showQuarters = ref(false)
const quarterTotals = computed(() => {
  const q = [0, 0, 0, 0]
  monthly.value.forEach((m, i) => {
    q[Math.floor(i / 3)] += m.total
  })
  return q
})

// ---- Agrupado del gráfico: mes / quarter / año ----
const groupBy = ref('mes')
const chartBuckets = computed(() => {
  if (groupBy.value === 'quarter') {
    const q = Array.from({ length: 4 }, (_, i) => ({ label: 'Q' + (i + 1), total: 0, count: 0, wonAmt: 0, projAmt: 0, wonNuevaAmt: 0, wonRenovAmt: 0, projNuevaAmt: 0, projRenovAmt: 0 }))
    monthly.value.forEach((m, i) => {
      const b = q[Math.floor(i / 3)]
      b.total += m.total; b.count += m.count; b.wonAmt += m.wonAmt; b.projAmt += m.projAmt
      b.wonNuevaAmt += m.wonNuevaAmt; b.wonRenovAmt += m.wonRenovAmt
      b.projNuevaAmt += m.projNuevaAmt; b.projRenovAmt += m.projRenovAmt
    })
    return q
  }
  if (groupBy.value === 'anio') {
    const by = {}
    for (const d of deals.value) {
      const dt = dealDate(d)
      if (!dt) continue
      if (!passesFilters(d)) continue
      const isWon = d.status === 'Won'
      const isProj = PROJ_STATUSES.includes(d.status)
      if (!isWon && !isProj) continue
      const y = Number(String(dt).slice(0, 4))
      if (!y) continue
      const b = by[y] || (by[y] = { label: String(y), year: y, total: 0, count: 0, wonAmt: 0, projAmt: 0, wonNuevaAmt: 0, wonRenovAmt: 0, projNuevaAmt: 0, projRenovAmt: 0 })
      const val = Number(d[amount.value]) || 0
      b.total += val; b.count += 1
      if (isWon) { b.wonAmt += val; if (isRenov(d)) b.wonRenovAmt += val; else b.wonNuevaAmt += val }
      else { b.projAmt += val; if (isRenov(d)) b.projRenovAmt += val; else b.projNuevaAmt += val }
    }
    return Object.values(by).sort((a, b) => a.year - b.year)
  }
  return monthly.value.map((m, i) => ({ ...m, label: MONTHS[i] }))
})
const maxBucket = computed(() => Math.max(1, ...chartBuckets.value.map((b) => b.total)))
function bucketBarHeight(v) {
  const pct = (v / maxBucket.value) * 100
  return (v > 0 ? Math.max(2, pct) : 0) + '%'
}

// ---- KPIs anuales de cierre + ranking (Dashboard Comercial) ----
function passTC(d) {
  const t = d.custom_tipo_oportunidad || ''
  if (tipoFilter.value === 'venta' && !t.startsWith('Nuevo')) return false
  if (tipoFilter.value === 'renovacion' && !t.startsWith('Renov')) return false
  if (tipoFilter.value === 'servicio' && !t.startsWith('Servicio')) return false
  if (canalFilter.value && (d.custom_canal || '') !== canalFilter.value) return false
  if (productFilter.value && (d.custom_producto || '') !== productFilter.value) return false
  return true
}
function inYearStr(str) {
  return str && Number(String(str).slice(0, 4)) === year.value
}
const kpi = computed(() => {
  let wonAmt = 0, wonCnt = 0, openAmt = 0, openCnt = 0, lostAmt = 0, lostCnt = 0
  for (const d of deals.value) {
    if (!passTC(d)) continue
    if (respFilter.value && d.deal_owner !== respFilter.value) continue
    const a = Number(d[amount.value]) || 0
    if (d.status === 'Won' && inYearStr(d.closed_date)) { wonAmt += a; wonCnt++ }
    else if (d.status === 'Lost' && inYearStr(d.closed_date || d.expected_closure_date)) { lostAmt += a; lostCnt++ }
    else if (d.status !== 'Won' && d.status !== 'Lost' && inYearStr(d.expected_closure_date)) { openAmt += a; openCnt++ }
  }
  const ticket = wonCnt ? wonAmt / wonCnt : 0
  const closed = wonCnt + lostCnt
  const winRate = closed ? Math.round((wonCnt / closed) * 100) : 0
  return { wonAmt, wonCnt, openAmt, openCnt, lostAmt, lostCnt, ticket, winRate }
})
const ranking = computed(() => {
  const by = {}
  for (const d of deals.value) {
    if (!passTC(d)) continue
    const o = d.deal_owner || '—'
    const r = by[o] || (by[o] = { owner: o, wonAmt: 0, wonCnt: 0, openAmt: 0, lostCnt: 0 })
    const a = Number(d[amount.value]) || 0
    if (d.status === 'Won' && inYearStr(d.closed_date)) { r.wonAmt += a; r.wonCnt++ }
    else if (d.status === 'Lost' && inYearStr(d.closed_date || d.expected_closure_date)) { r.lostCnt++ }
    else if (d.status !== 'Won' && d.status !== 'Lost' && inYearStr(d.expected_closure_date)) { r.openAmt += a }
  }
  return Object.values(by)
    .map((r) => {
      const closed = r.wonCnt + r.lostCnt
      return {
        ...r,
        winRate: closed ? Math.round((r.wonCnt / closed) * 100) : 0,
        ticket: r.wonCnt ? r.wonAmt / r.wonCnt : 0,
        total: r.wonAmt + r.openAmt,
      }
    })
    .filter((r) => r.wonCnt || r.openAmt || r.lostCnt)
    .sort((a, b) => b.wonAmt - a.wonAmt)
})

const showNoDate = computed(() => includeNoDate.value && noDate.value.count > 0)

// Selección de barra -> lista de oportunidades que la componen
// null | 0..11 (índice de mes) | 'nodate'
const selected = ref(null)
function selectBucket(key) {
  selected.value = selected.value === key ? null : key
}
const selectedLabel = computed(() => {
  if (selected.value === null) return ''
  if (selected.value === 'nodate') return 'Sin fecha de cierre'
  return (MONTHS_FULL[selected.value] || '') + ' ' + year.value
})
const selectedDeals = computed(() => {
  if (selected.value === null) return []
  const out = []
  for (const d of deals.value) {
    if (!passesFilters(d)) continue
    const isWon = d.status === 'Won'
    const isProj = PROJ_STATUSES.includes(d.status)
    if (!isWon && !isProj) continue
    const dt = dealDate(d)
    if (selected.value === 'nodate') {
      if (dt) continue
    } else {
      if (!dt) continue
      if (Number(dt.slice(0, 4)) !== year.value) continue
      if (Number(dt.slice(5, 7)) - 1 !== selected.value) continue
    }
    out.push(d)
  }
  return out.sort(
    (a, b) => (Number(b[amount.value]) || 0) - (Number(a[amount.value]) || 0),
  )
})
function openDeal(name) {
  router.push({ name: 'Deal', params: { dealId: name } })
}

const monthlyTotal = computed(() =>
  monthly.value.reduce((a, m) => a + m.total, 0),
)
const yearTotal = computed(() => monthlyTotal.value + noDate.value.total)
const yearCount = computed(
  () => monthly.value.reduce((a, m) => a + m.count, 0) + noDate.value.count,
)
const yearWon = computed(
  () => monthly.value.reduce((a, m) => a + m.won, 0) + noDate.value.won,
)
// monto ganado (verde) y monto de pipeline/proyectado (violeta) por separado
const yearWonAmt = computed(
  () => monthly.value.reduce((a, m) => a + m.wonAmt, 0) + noDate.value.wonAmt,
)
const yearProjAmt = computed(
  () => monthly.value.reduce((a, m) => a + m.projAmt, 0) + noDate.value.projAmt,
)
const yearOpen = computed(() => yearCount.value - yearWon.value)
const maxMonth = computed(() =>
  Math.max(1, ...monthly.value.map((m) => m.total), noDate.value.total),
)
const bestMonth = computed(() => {
  let idx = -1
  let total = 0
  monthly.value.forEach((m, i) => {
    if (m.total > total) {
      total = m.total
      idx = i
    }
  })
  return { idx, total }
})

function barHeight(v) {
  const pct = (v / maxMonth.value) * 100
  return (v > 0 ? Math.max(2, pct) : 0) + '%'
}
function money(n) {
  const v = Number(n) || 0
  return '$' + Math.round(v).toLocaleString('es-AR')
}
function moneyShort(n) {
  const v = Number(n) || 0
  if (v >= 1000000) return '$' + (v / 1000000).toFixed(1) + 'M'
  if (v >= 1000) return '$' + Math.round(v / 1000) + 'k'
  return '$' + Math.round(v)
}
</script>
