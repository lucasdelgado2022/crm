<template>
  <LayoutHeader v-if="organization.doc">
    <template #left-header>
      <Breadcrumbs :items="breadcrumbs">
        <template #prefix="{ item }">
          <Icon v-if="item.icon" :icon="item.icon" class="mr-2 h-4" />
        </template>
      </Breadcrumbs>
    </template>
    <template #right-header>
      <CustomActions
        v-if="organization._actions?.length"
        :actions="organization._actions"
      />
    </template>
  </LayoutHeader>
  <div v-if="organization.doc" ref="parentRef" class="flex h-full">
    <Resizer
      v-if="organization.doc"
      :parent="$refs.parentRef"
      class="flex h-full flex-col overflow-hidden border-r"
    >
      <div class="border-b">
        <FileUploader
          :validateFile="validateIsImageFile"
          @success="changeOrganizationImage"
        >
          <template #default="{ openFileSelector, error }">
            <div class="flex flex-col items-start justify-start gap-4 p-5">
              <div class="flex gap-4 items-center">
                <div class="group relative h-15.5 w-15.5">
                  <Avatar
                    size="3xl"
                    class="h-15.5 w-15.5"
                    :label="organization.doc.organization_name"
                    :image="organization.doc.organization_logo"
                  />
                  <component
                    :is="organization.doc.organization_logo ? Dropdown : 'div'"
                    v-bind="
                      organization.doc.organization_logo
                        ? {
                            options: [
                              {
                                icon: 'upload',
                                label: organization.doc.organization_logo
                                  ? __('Change Image')
                                  : __('Upload Image'),
                                onClick: openFileSelector,
                              },
                              {
                                icon: 'trash-2',
                                label: __('Remove Image'),
                                onClick: () => changeOrganizationImage(''),
                              },
                            ],
                          }
                        : { onClick: openFileSelector }
                    "
                    class="!absolute bottom-0 left-0 right-0"
                  >
                    <div
                      class="z-1 absolute bottom-0 left-0 right-0 flex h-14 cursor-pointer items-center justify-center rounded-b-full bg-black bg-opacity-40 pt-5 opacity-0 duration-300 ease-in-out group-hover:opacity-100"
                      style="
                        -webkit-clip-path: inset(22px 0 0 0);
                        clip-path: inset(22px 0 0 0);
                      "
                    >
                      <CameraIcon class="h-6 w-6 cursor-pointer text-white" />
                    </div>
                  </component>
                </div>
                <div class="flex flex-col gap-2 truncate">
                  <div class="truncate text-3xl-medium uppercase text-ink-gray-9">
                    <span>{{ organization.doc.name }}</span>
                  </div>
                  <div
                    v-if="organization.doc.website"
                    class="flex w-fit cursor-pointer items-center gap-1.5 text-base text-ink-gray-8 hover:text-ink-gray-9 hover:underline"
                    :title="__('Open Website')"
                    @click="openWebsite"
                  >
                    <WebsiteIcon class="size-4" />
                    <span>{{ website(organization.doc.website) }}</span>
                  </div>
                  <button
                    v-if="organization.doc.website"
                    class="flex w-fit items-center gap-1.5 text-sm text-ink-gray-5 hover:text-ink-gray-8"
                    :title="__('Traer el logo desde el dominio del sitio web')"
                    @click="traerLogo"
                  >
                    <FeatherIcon
                      :name="logoLoading ? 'loader' : 'image'"
                      class="h-3.5 w-3.5"
                      :class="{ 'animate-spin': logoLoading }"
                    />
                    {{ __('Traer logo') }}
                  </button>
                  <div class="flex items-center gap-3">
                    <Link
                      doctype="CRM Territory"
                      :value="organization.doc.territory"
                      @change="(v) => organization.setValue.submit({ territory: v })"
                    >
                      <template #target="{ togglePopover }">
                        <button
                          class="flex items-center gap-1.5 rounded-full border border-outline-gray-2 px-2.5 py-1 text-sm text-ink-gray-7 hover:bg-surface-gray-2"
                          @click.stop="togglePopover()"
                        >
                          <FeatherIcon name="globe" class="h-3.5 w-3.5" />
                          <span
                            :class="{
                              'text-ink-gray-4': !organization.doc.territory,
                            }"
                          >
                            {{ organization.doc.territory || __('País') }}
                          </span>
                          <FeatherIcon
                            name="chevron-down"
                            class="h-3.5 w-3.5 text-ink-gray-5"
                          />
                        </button>
                      </template>
                    </Link>
                    <RatingInput
                      :value="organization.doc.custom_chance"
                      :max="5"
                      @change="
                        (v) => organization.setValue.submit({ custom_chance: v })
                      "
                    />
                  </div>
                  <ErrorMessage :message="__(error)" />
                </div>
              </div>
            </div>
          </template>
        </FileUploader>
      </div>
      <div v-if="organization.doc" class="shrink-0 px-3 pb-1">
        <OrganizationLocation
          :key="organization.doc.name"
          :docname="organization.doc.name"
          :google-maps="organization.doc.custom_google_maps"
          :coordenadas="organization.doc.custom_coordenadas"
        />
      </div>
      <div
        v-if="sections.data"
        class="flex flex-1 flex-col justify-between overflow-hidden"
      >
        <SidePanelLayout
          :sections="sections.data"
          doctype="CRM Organization"
          :docname="organization.doc.name"
          @reload="sections.reload"
          @beforeFieldChange="beforeFieldChange"
        />
      </div>
      <div v-if="canDelete" class="shrink-0 border-t p-3">
        <Button
          :label="__('Delete')"
          theme="red"
          size="sm"
          iconLeft="trash-2"
          class="w-full"
          @click="deleteOrganization()"
        />
      </div>
    </Resizer>
    <div class="flex flex-1 flex-col gap-4 overflow-hidden p-4 sm:p-5">
      <!-- Widget: Oportunidades -->
      <div
        :class="
          widgetShown('Deals')
            ? 'flex min-h-0 flex-1 flex-col rounded-lg border'
            : 'flex shrink-0 flex-col rounded-lg border'
        "
      >
        <div
          class="flex shrink-0 items-center gap-3 border-b px-4 py-3"
        >
          <div
            class="flex shrink-0 items-center gap-2 text-base font-semibold text-ink-gray-8"
          >
            <DealsIcon class="h-5" />
            {{ __('Deals') }}
            <Badge variant="subtle" theme="gray" size="sm">
              {{ dealRows.length }}
            </Badge>
          </div>
          <div
            v-if="dealStatusCounts.length && widgetShown('Deals')"
            class="flex min-w-0 flex-1 flex-wrap items-center gap-2"
          >
            <button
              class="flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-sm"
              :class="
                dealStatusFilter === null
                  ? 'border-outline-gray-3 bg-surface-gray-2 text-ink-gray-9'
                  : 'border-outline-gray-2 text-ink-gray-6 hover:text-ink-gray-9'
              "
              @click="dealStatusFilter = null"
            >
              {{ __('Todos') }}
              <span class="text-ink-gray-5">{{ deals.data?.length || 0 }}</span>
            </button>
            <button
              v-for="s in dealStatusCounts"
              :key="s.status"
              class="flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-sm"
              :class="
                dealStatusFilter === s.status
                  ? 'border-outline-gray-3 bg-surface-gray-2 text-ink-gray-9'
                  : 'border-outline-gray-2 text-ink-gray-6 hover:text-ink-gray-9'
              "
              @click="
                dealStatusFilter = dealStatusFilter === s.status ? null : s.status
              "
            >
              <IndicatorIcon :class="s.color" />
              {{ s.status }}
              <span class="text-ink-gray-5">{{ s.count }}</span>
            </button>
          </div>
          <div class="flex shrink-0 gap-2" :class="{ 'ml-auto': !(dealStatusCounts.length && widgetShown('Deals')) }">
            <Link
              value=""
              doctype="CRM Deal"
              :onCreate="(v, close) => { createNew('Deals'); close && close() }"
              @change="(name) => addExisting('Deals', name)"
            >
              <template #target="{ togglePopover }">
                <Button variant="outline" @click="togglePopover()">
                  <template #prefix>
                    <FeatherIcon name="link" class="h-4" />
                  </template>
                  {{ __('Add') }}
                </Button>
              </template>
            </Link>
            <Button
              variant="ghost"
              :tooltip="maxWidget === 'Deals' ? __('Restaurar') : __('Maximizar')"
              @click="toggleMax('Deals')"
            >
              <template #icon>
                <component
                  :is="maxWidget === 'Deals' ? MinimizeIcon : MaximizeIcon"
                  class="h-4 w-4"
                />
              </template>
            </Button>
          </div>
        </div>
        <div v-show="widgetShown('Deals')" class="min-h-0 flex-1 overflow-y-auto">
          <DealsListView
            v-if="dealRows.length"
            class="py-2"
            :rows="dealRows"
            :columns="dealColumns"
            :options="{ selectable: false, showTooltip: false }"
          />
          <EmptyState v-else :icon="DealsIcon" :name="__('Deals')" />
        </div>
      </div>

      <!-- Widget: Leads -->
      <div
        :class="
          widgetShown('Leads')
            ? 'flex min-h-0 flex-1 flex-col rounded-lg border'
            : 'flex shrink-0 flex-col rounded-lg border'
        "
      >
        <div class="flex shrink-0 items-center gap-3 border-b px-4 py-3">
          <div
            class="flex shrink-0 items-center gap-2 text-base font-semibold text-ink-gray-8"
          >
            <LeadsIcon class="h-5" />
            {{ __('Leads') }}
            <Badge variant="subtle" theme="gray" size="sm">
              {{ leadRows.length }}
            </Badge>
          </div>
          <div
            v-if="leadStatusCounts.length && widgetShown('Leads')"
            class="flex min-w-0 flex-1 flex-wrap items-center gap-2"
          >
            <button
              class="flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-sm"
              :class="
                leadStatusFilter === null
                  ? 'border-outline-gray-3 bg-surface-gray-2 text-ink-gray-9'
                  : 'border-outline-gray-2 text-ink-gray-6 hover:text-ink-gray-9'
              "
              @click="leadStatusFilter = null"
            >
              {{ __('Todos') }}
              <span class="text-ink-gray-5">{{ leads.data?.length || 0 }}</span>
            </button>
            <button
              v-for="s in leadStatusCounts"
              :key="s.status"
              class="flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-sm"
              :class="
                leadStatusFilter === s.status
                  ? 'border-outline-gray-3 bg-surface-gray-2 text-ink-gray-9'
                  : 'border-outline-gray-2 text-ink-gray-6 hover:text-ink-gray-9'
              "
              @click="
                leadStatusFilter = leadStatusFilter === s.status ? null : s.status
              "
            >
              <IndicatorIcon :class="s.color" />
              {{ s.status }}
              <span class="text-ink-gray-5">{{ s.count }}</span>
            </button>
          </div>
          <div
            class="flex shrink-0 gap-2"
            :class="{
              'ml-auto': !(leadStatusCounts.length && widgetShown('Leads')),
            }"
          >
            <Button
              variant="ghost"
              :tooltip="maxWidget === 'Leads' ? __('Restaurar') : __('Maximizar')"
              @click="toggleMax('Leads')"
            >
              <template #icon>
                <component
                  :is="maxWidget === 'Leads' ? MinimizeIcon : MaximizeIcon"
                  class="h-4 w-4"
                />
              </template>
            </Button>
          </div>
        </div>
        <div
          v-show="widgetShown('Leads')"
          class="min-h-0 flex-1 overflow-y-auto"
        >
          <LeadsListView
            v-if="leadRows.length"
            class="py-2"
            :rows="leadRows"
            :columns="leadColumns"
            :options="{ selectable: false, showTooltip: false }"
          />
          <EmptyState v-else :icon="LeadsIcon" :name="__('Leads')" />
        </div>
      </div>

      <!-- Widget: Contacts -->
      <div
        :class="
          widgetShown('Contacts')
            ? 'flex min-h-0 flex-1 flex-col rounded-lg border'
            : 'flex shrink-0 flex-col rounded-lg border'
        "
      >
        <div
          class="flex shrink-0 items-center gap-3 border-b px-4 py-3"
        >
          <div
            class="flex shrink-0 items-center gap-2 text-base font-semibold text-ink-gray-8"
          >
            <ContactsIcon class="h-5" />
            {{ __('Contacts') }}
            <Badge variant="subtle" theme="gray" size="sm">
              {{ contactRows.length }}
            </Badge>
          </div>
          <div
            v-if="contactRolCounts.length > 1 && widgetShown('Contacts')"
            class="flex min-w-0 flex-1 flex-wrap items-center gap-2"
          >
            <button
              class="flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-sm"
              :class="
                contactRolFilter === null
                  ? 'border-outline-gray-3 bg-surface-gray-2 text-ink-gray-9'
                  : 'border-outline-gray-2 text-ink-gray-6 hover:text-ink-gray-9'
              "
              @click="contactRolFilter = null"
            >
              {{ __('Todos') }}
              <span class="text-ink-gray-5">{{ contacts.data?.length || 0 }}</span>
            </button>
            <button
              v-for="r in contactRolCounts"
              :key="r.rol"
              class="flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-sm"
              :class="
                contactRolFilter === r.rol
                  ? 'border-outline-gray-3 bg-surface-gray-2 text-ink-gray-9'
                  : 'border-outline-gray-2 text-ink-gray-6 hover:text-ink-gray-9'
              "
              @click="contactRolFilter = contactRolFilter === r.rol ? null : r.rol"
            >
              {{ r.rol }}
              <span class="text-ink-gray-5">{{ r.count }}</span>
            </button>
          </div>
          <div
            class="flex shrink-0 gap-2"
            :class="{
              'ml-auto': !(contactRolCounts.length > 1 && widgetShown('Contacts')),
            }"
          >
            <Link
              value=""
              doctype="Contact"
              :onCreate="(v, close) => { createNew('Contacts'); close && close() }"
              @change="(name) => addExisting('Contacts', name)"
            >
              <template #target="{ togglePopover }">
                <Button variant="outline" @click="togglePopover()">
                  <template #prefix>
                    <FeatherIcon name="link" class="h-4" />
                  </template>
                  {{ __('Add') }}
                </Button>
              </template>
            </Link>
            <Button
              variant="ghost"
              :tooltip="
                maxWidget === 'Contacts' ? __('Restaurar') : __('Maximizar')
              "
              @click="toggleMax('Contacts')"
            >
              <template #icon>
                <component
                  :is="maxWidget === 'Contacts' ? MinimizeIcon : MaximizeIcon"
                  class="h-4 w-4"
                />
              </template>
            </Button>
          </div>
        </div>
        <div
          v-show="widgetShown('Contacts')"
          class="min-h-0 flex-1 overflow-y-auto"
        >
          <ContactsListView
            v-if="contactRows.length"
            class="py-2"
            :rows="contactRows"
            :columns="contactColumns"
            :options="{ selectable: false, showTooltip: false }"
          />
          <EmptyState v-else :icon="ContactsIcon" :name="__('Contacts')" />
        </div>
      </div>

      <!-- Widget: Software -->
      <div
        :class="
          widgetShown('Software')
            ? 'flex min-h-0 flex-1 flex-col rounded-lg border'
            : 'flex shrink-0 flex-col rounded-lg border'
        "
      >
        <div
          class="flex shrink-0 items-center justify-between gap-2 border-b px-4 py-3"
        >
          <div
            class="flex items-center gap-2 text-base font-semibold text-ink-gray-8"
          >
            <SoftwareIcon class="h-5" />
            {{ __('Software') }}
            <Badge variant="subtle" theme="gray" size="sm">
              {{ softwareRows.length }}
            </Badge>
          </div>
          <div class="flex gap-2">
            <Dropdown :options="[...softwareLinkOptions, ...softwareCreateOptions]">
              <Button variant="outline">
                <template #prefix>
                  <FeatherIcon name="link" class="h-4" />
                </template>
                {{ __('Add') }}
                <template #suffix>
                  <FeatherIcon name="chevron-down" class="h-4" />
                </template>
              </Button>
            </Dropdown>
            <Button
              variant="ghost"
              :tooltip="
                maxWidget === 'Software' ? __('Restaurar') : __('Maximizar')
              "
              @click="toggleMax('Software')"
            >
              <template #icon>
                <component
                  :is="maxWidget === 'Software' ? MinimizeIcon : MaximizeIcon"
                  class="h-4 w-4"
                />
              </template>
            </Button>
          </div>
        </div>
        <div
          v-show="widgetShown('Software')"
          class="min-h-0 flex-1 overflow-y-auto"
        >
          <ListView
            v-if="softwareRows.length"
            class="px-4 py-2"
            :rows="softwareRows"
            :columns="softwareColumns"
            row-key="name"
            :options="{ selectable: false, showTooltip: false }"
          >
            <template #cell="{ item, row, column }">
              <Button
                v-if="column.key === '_unlink'"
                variant="ghost"
                class="!h-6 !w-6"
                :tooltip="__('Desvincular')"
                @click.stop.prevent="unlinkSoftware(row)"
              >
                <FeatherIcon name="x" class="h-4 w-4 text-ink-gray-6" />
              </Button>
              <div v-else class="truncate text-base">
                {{ item?.timeAgo || item?.label || item }}
              </div>
            </template>
          </ListView>
          <EmptyState v-else :icon="SoftwareIcon" :name="__('Software')" />
        </div>
      </div>

      <!-- Widget: Datos / Hechos (con investigacion IA) -->
      <div
        :class="
          widgetShown('Facts')
            ? 'flex min-h-0 flex-1 flex-col rounded-lg border'
            : 'flex shrink-0 flex-col rounded-lg border'
        "
      >
        <div
          class="flex shrink-0 items-center justify-between gap-2 border-b px-4 py-3"
        >
          <div
            class="flex items-center gap-2 text-base font-semibold text-ink-gray-8"
          >
            <FeatherIcon name="file-text" class="h-5" />
            {{ __('Datos / Hechos') }}
            <Badge variant="subtle" theme="gray" size="sm">
              {{ facts.data?.length || 0 }}
            </Badge>
          </div>
          <div class="flex gap-2">
            <Button variant="subtle" :loading="aiLoading" @click="investigarIA">
              <template #prefix>
                <FeatherIcon name="zap" class="h-4" />
              </template>
              {{ __('Investigar con IA') }}
            </Button>
            <Button variant="outline" @click="showAddFact = !showAddFact">
              <template #prefix>
                <FeatherIcon name="plus" class="h-4" />
              </template>
              {{ __('Agregar') }}
            </Button>
            <Button
              variant="ghost"
              :tooltip="maxWidget === 'Facts' ? __('Restaurar') : __('Maximizar')"
              @click="toggleMax('Facts')"
            >
              <template #icon>
                <component
                  :is="maxWidget === 'Facts' ? MinimizeIcon : MaximizeIcon"
                  class="h-4 w-4"
                />
              </template>
            </Button>
          </div>
        </div>
        <div
          v-show="widgetShown('Facts')"
          class="min-h-0 flex-1 overflow-y-auto p-4"
        >
          <div v-if="showAddFact" class="mb-3 rounded-lg border p-3">
            <textarea
              v-model="newFact.hecho"
              :placeholder="__('Hecho / dato...')"
              rows="2"
              class="w-full rounded border border-outline-gray-2 bg-surface-base p-2 text-sm text-ink-gray-8 focus:outline-none"
            />
            <input
              v-model="newFact.fuente"
              :placeholder="__('Fuente (URL o descripción)')"
              class="mt-2 w-full rounded border border-outline-gray-2 bg-surface-base p-2 text-sm text-ink-gray-8 focus:outline-none"
            />
            <div class="mt-2 flex justify-end gap-2">
              <Button variant="ghost" @click="showAddFact = false">
                {{ __('Cancelar') }}
              </Button>
              <Button
                variant="solid"
                :disabled="!newFact.hecho.trim()"
                @click="addFact"
              >
                {{ __('Guardar') }}
              </Button>
            </div>
          </div>
          <div v-if="facts.data?.length" class="flex flex-col gap-2">
            <div
              v-for="f in facts.data"
              :key="f.name"
              class="group flex items-start gap-2 rounded-lg border p-2.5"
            >
              <span
                class="mt-0.5 shrink-0 rounded px-1.5 py-0.5 text-xs font-medium"
                :class="
                  f.origen === 'IA'
                    ? 'bg-violet-100 text-violet-700'
                    : 'bg-surface-gray-2 text-ink-gray-6'
                "
                >{{ f.origen === 'IA' ? 'IA' : 'Manual' }}</span
              >
              <div class="min-w-0 flex-1">
                <div class="whitespace-pre-line text-sm text-ink-gray-8">
                  {{ f.hecho }}
                </div>
                <a
                  v-if="f.fuente && /^https?:/.test(f.fuente)"
                  :href="f.fuente"
                  target="_blank"
                  class="block truncate text-xs text-blue-600 hover:underline"
                  >{{ f.fuente }}</a
                >
                <div
                  v-else-if="f.fuente"
                  class="truncate text-xs text-ink-gray-5"
                >
                  {{ f.fuente }}
                </div>
              </div>
              <button
                class="shrink-0 rounded p-1 text-ink-gray-4 opacity-0 hover:bg-surface-gray-2 hover:text-ink-red-6 group-hover:opacity-100"
                @click="deleteFact(f.name)"
              >
                <FeatherIcon name="x" class="h-3.5 w-3.5" />
              </button>
            </div>
          </div>
          <div
            v-else
            class="flex h-24 items-center justify-center px-4 text-center text-sm text-ink-gray-4"
          >
            {{ __('Sin datos aún. Usá "Investigar con IA" o "Agregar".') }}
          </div>
        </div>
      </div>
    </div>
  </div>
  <ErrorPage
    v-else-if="errorTitle"
    :errorTitle="errorTitle"
    :errorMessage="errorMessage"
  />
  <DeleteLinkedDocModal
    v-if="showDeleteLinkedDocModal"
    v-model="showDeleteLinkedDocModal"
    :doctype="'CRM Organization'"
    :docname="props.organizationId"
    name="Organizations"
  />
  <DealModal
    v-if="showDealModal"
    v-model="showDealModal"
    :defaults="{ organization: props.organizationId }"
  />
  <ContactModal
    v-if="showContactModal"
    v-model="showContactModal"
    :contact="{ company_name: props.organizationId }"
    :options="{
      redirect: false,
      afterInsert: () => contacts.reload(),
    }"
  />
  <Dialog
    v-model="showLinkSoftwareDialog"
    :options="{ title: __('Add Existing') + ': ' + __(linkSoftwareLabel) }"
  >
    <template #body-content>
      <Link
        class="form-control"
        value=""
        :doctype="linkSoftwareDoctype"
        @change="(name) => linkSoftware(name)"
      />
    </template>
  </Dialog>
</template>

<script setup>
import ErrorPage from '@/components/ErrorPage.vue'
import Resizer from '@/components/Resizer.vue'
import SidePanelLayout from '@/components/SidePanelLayout.vue'
import OrganizationLocation from '@/components/OrganizationLocation.vue'
import Icon from '@/components/Icon.vue'
import LayoutHeader from '@/components/LayoutHeader.vue'
import DealsListView from '@/components/ListViews/DealsListView.vue'
import LeadsListView from '@/components/ListViews/LeadsListView.vue'
import ContactsListView from '@/components/ListViews/ContactsListView.vue'
import WebsiteIcon from '@/components/Icons/WebsiteIcon.vue'
import CameraIcon from '@/components/Icons/CameraIcon.vue'
import DealsIcon from '@/components/Icons/DealsIcon.vue'
import LeadsIcon from '@/components/Icons/LeadsIcon.vue'
import ContactsIcon from '@/components/Icons/ContactsIcon.vue'
import IndicatorIcon from '@/components/Icons/IndicatorIcon.vue'
import RatingInput from '@/components/Controls/RatingInput.vue'
import MaximizeIcon from '@/components/Icons/MaximizeIcon.vue'
import MinimizeIcon from '@/components/Icons/MinimizeIcon.vue'
import DeleteLinkedDocModal from '@/components/DeleteLinkedDocModal.vue'
import DealModal from '@/components/Modals/DealModal.vue'
import ContactModal from '@/components/Modals/ContactModal.vue'
import Link from '@/components/Controls/Link.vue'
import CustomActions from '@/components/CustomActions.vue'
import { useDocument } from '@/data/document'
import { getSettings } from '@/stores/settings'
import { globalStore } from '@/stores/global'
import { getMeta } from '@/stores/meta'
import { usersStore } from '@/stores/users'
import { statusesStore } from '@/stores/statuses'
import { getView } from '@/utils/view'
import {
  validateIsImageFile,
  setupCustomizations,
  openWebsite as openExternalWebsite,
} from '@/utils'
import { timestampCell } from '@/composables/useTimelinePreferences'
import {
  Breadcrumbs,
  Avatar,
  FileUploader,
  Dropdown,
  Dialog,
  Tabs,
  ListView,
  FeatherIcon,
  createListResource,
  usePageMeta,
  createResource,
  toast,
  call,
} from 'frappe-ui'
import { useDoctypeModal } from '@/composables/doctypeModal'
import { useTelemetry } from 'frappe-ui/frappe'
import { computed, h, ref, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const props = defineProps({
  organizationId: { type: String, required: true },
})

const { brand } = getSettings()
const { $dialog, $socket } = globalStore()
const { getUser } = usersStore()
const { getDealStatus, getLeadStatus } = statusesStore()
const { doctypeMeta } = getMeta('CRM Organization')
const { capture } = useTelemetry()

const route = useRoute()
const router = useRouter()

const errorTitle = ref('')
const errorMessage = ref('')

const showDeleteLinkedDocModal = ref(false)

// Maximizar widget (deja solo los encabezados de los demas)
const maxWidget = ref(null)
function toggleMax(key) {
  maxWidget.value = maxWidget.value === key ? null : key
}
function widgetShown(key) {
  return !maxWidget.value || maxWidget.value === key
}

// Widget Datos / Hechos (+ investigacion IA)
const facts = createListResource({
  type: 'list',
  doctype: 'CRM Fact',
  cache: ['facts', props.organizationId],
  fields: ['name', 'hecho', 'fuente', 'origen', 'modified'],
  filters: { organization: props.organizationId },
  orderBy: 'modified desc',
  pageLength: 100,
  auto: true,
})
const showAddFact = ref(false)
const newFact = ref({ hecho: '', fuente: '' })
async function addFact() {
  if (!newFact.value.hecho.trim()) return
  try {
    await call('frappe.client.insert', {
      doc: {
        doctype: 'CRM Fact',
        organization: props.organizationId,
        hecho: newFact.value.hecho,
        fuente: newFact.value.fuente,
        origen: 'Manual',
      },
    })
    newFact.value = { hecho: '', fuente: '' }
    showAddFact.value = false
    facts.reload()
    toast.success(__('Dato agregado'))
  } catch (e) {
    toast.error(e.messages?.[0] || __('No se pudo guardar'))
  }
}
async function deleteFact(name) {
  try {
    await call('frappe.client.delete', { doctype: 'CRM Fact', name })
    facts.reload()
  } catch (e) {
    toast.error(e.messages?.[0] || __('No se pudo eliminar'))
  }
}
const aiLoading = ref(false)
async function investigarIA() {
  aiLoading.value = true
  try {
    const res = await call('crm.api.ai_research.investigar_organizacion', {
      organization: props.organizationId,
    })
    facts.reload()
    toast.success(__('IA: {0} hechos agregados', [res?.creados ?? 0]))
  } catch (e) {
    toast.error(e.messages?.[0] || __('No se pudo investigar con IA'))
  } finally {
    aiLoading.value = false
  }
}

// #3 Traer logo de marca desde el dominio del sitio web
const logoLoading = ref(false)
function traerLogo() {
  const web = organization.doc?.website
  if (!web) {
    toast.error(__('La organización no tiene sitio web'))
    return
  }
  const domain = String(web)
    .replace(/^https?:\/\//i, '')
    .replace(/^www\./i, '')
    .split('/')[0]
    .trim()
  if (!domain) {
    toast.error(__('No se pudo determinar el dominio'))
    return
  }
  logoLoading.value = true
  const clearbit = 'https://logo.clearbit.com/' + domain
  const favicon =
    'https://www.google.com/s2/favicons?domain=' + domain + '&sz=128'
  const img = new Image()
  img.onload = () => setLogo(clearbit)
  img.onerror = () => setLogo(favicon)
  img.src = clearbit
}
function setLogo(url) {
  organization.setValue
    .submit({ organization_logo: url })
    .then(() => toast.success(__('Logo actualizado')))
    .catch(() => toast.error(__('No se pudo guardar el logo')))
    .finally(() => {
      logoLoading.value = false
    })
}

const {
  document: organization,
  permissions,
  scripts,
  triggerOnRender,
} = useDocument('CRM Organization', props.organizationId)

const canDelete = computed(() => permissions.data?.permissions?.delete || false)

onMounted(async () => {
  if (organization.doc) await triggerOnRender()
})

const breadcrumbs = computed(() => {
  let items = [{ label: __('Organizations'), route: { name: 'Organizations' } }]

  if (route.query.view || route.query.viewType) {
    let view = getView(
      route.query.view,
      route.query.viewType,
      'CRM Organization',
    )
    if (view) {
      items.push({
        label: __(view.label),
        icon: view.icon,
        route: {
          name: 'Organizations',
          params: { viewType: route.query.viewType },
          query: { view: route.query.view },
        },
      })
    }
  }

  items.push({
    label: title.value,
    route: {
      name: 'Organization',
      params: { organizationId: props.organizationId },
    },
  })
  return items
})

const title = computed(() => {
  let t = doctypeMeta.value?.title_field || 'name'
  return organization.doc?.[t] || props.organizationId
})

usePageMeta(() => {
  return {
    title: title.value,
    icon: brand.favicon,
  }
})

async function deleteOrganization() {
  showDeleteLinkedDocModal.value = true
}

function changeOrganizationImage(file) {
  organization.setValue.submit({
    organization_logo: file?.file_url || null,
  })
}

function beforeFieldChange(data) {
  if (Object.hasOwn(data ?? {}, 'organization_name')) {
    call('frappe.client.rename_doc', {
      doctype: 'CRM Organization',
      old_name: props.organizationId,
      new_name: data.organization_name,
    }).then(() => {
      router.push({
        name: 'Organization',
        params: { organizationId: data.organization_name },
      })
    })
  } else {
    organization.save.submit()
  }
}

function website(url) {
  return url && url.replace(/^(?:https?:\/\/)?(?:www\.)?/i, '')
}

function openWebsite() {
  if (!organization.doc.website) {
    toast.error(__('No Website Found'))
    return
  }

  openExternalWebsite(organization.doc.website)
}

const sections = createResource({
  url: 'crm.fcrm.doctype.crm_fields_layout.crm_fields_layout.get_sidepanel_sections',
  cache: ['sidePanelSections', 'CRM Organization'],
  params: { doctype: 'CRM Organization' },
  auto: true,
  transform: (data) => getParsedSections(data),
})

function getParsedSections(_sections) {
  return _sections.map((section) => {
    section.columns = section.columns.map((column) => {
      column.fields = column.fields.map((field) => {
        if (field.fieldname === 'address') {
          return {
            ...field,
            create: (value, close) => {
              showAddressModal()
              close()
            },
            edit: (address) => showAddressModal(address),
          }
        } else {
          return field
        }
      })
      return column
    })
    return section
  })
}

const SoftwareIcon = {
  render: () => h(FeatherIcon, { name: 'monitor', class: 'h-5 w-5' }),
}

// #47: todos los deals de la organizacion, visibles (solo lectura) para cualquier
// usuario del CRM (evita el filtro de jerarquia solo en este widget).
const deals = createResource({
  url: 'crm.api.doc.get_organization_deals',
  params: {
    organization: props.organizationId,
  },
  cache: ['org-deals', props.organizationId],
  auto: true,
})

const leads = createListResource({
  type: 'list',
  doctype: 'CRM Lead',
  cache: ['leads', props.organizationId],
  fields: [
    'name',
    'lead_name',
    'first_name',
    'last_name',
    'organization',
    'status',
    'email',
    'mobile_no',
    'lead_owner',
    'modified',
  ],
  filters: {
    organization: props.organizationId,
  },
  orderBy: 'modified desc',
  pageLength: 20,
  auto: true,
})

const contacts = createListResource({
  type: 'list',
  doctype: 'Contact',
  cache: ['contacts', props.organizationId],
  fields: [
    'name',
    'full_name',
    'first_name',
    'last_name',
    'image',
    'email_id',
    'mobile_no',
    'company_name',
    'custom_rol',
    'designation',
    'custom_engagement',
    'custom_relacion',
    'modified',
  ],
  filters: {
    company_name: props.organizationId,
  },
  orderBy: 'modified desc',
  pageLength: 20,
  auto: true,
})

const software = createListResource({
  type: 'list',
  doctype: 'Software',
  cache: ['software', props.organizationId],
  fields: ['name', 'software_name', 'custom_dominio', 'modified'],
  filters: [
    ['Software Organization', 'organization', '=', props.organizationId],
  ],
  orderBy: 'modified desc',
  pageLength: 99,
  auto: true,
})

const procesos = createListResource({
  type: 'list',
  doctype: 'Procesos - Tecnologias',
  cache: ['procesos', props.organizationId],
  fields: ['name', 'nombre', 'modified'],
  filters: {
    organization: props.organizationId,
  },
  orderBy: 'modified desc',
  pageLength: 99,
  auto: true,
})

const dealStatusFilter = ref(null)

const dealStatusCounts = computed(() => {
  const counts = {}
  for (const d of deals.data || []) {
    if (!d.status) continue
    counts[d.status] = (counts[d.status] || 0) + 1
  }
  return Object.entries(counts)
    .map(([status, count]) => ({
      status,
      count,
      color: getDealStatus(status)?.color,
      position: getDealStatus(status)?.position ?? 999,
    }))
    .sort((a, b) => a.position - b.position)
})

const dealRows = computed(() => {
  let data = deals.data || []
  if (dealStatusFilter.value)
    data = data.filter((d) => d.status === dealStatusFilter.value)
  return data.map(getDealRowObject)
})
const leadStatusFilter = ref(null)

const leadStatusCounts = computed(() => {
  const counts = {}
  for (const l of leads.data || []) {
    if (!l.status) continue
    counts[l.status] = (counts[l.status] || 0) + 1
  }
  return Object.entries(counts)
    .map(([status, count]) => ({
      status,
      count,
      color: getLeadStatus(status)?.color,
      position: getLeadStatus(status)?.position ?? 999,
    }))
    .sort((a, b) => a.position - b.position)
})

const leadRows = computed(() => {
  let data = leads.data || []
  if (leadStatusFilter.value)
    data = data.filter((l) => l.status === leadStatusFilter.value)
  return data.map(getLeadRowObject)
})

const contactRolFilter = ref(null)

const contactRolCounts = computed(() => {
  const counts = {}
  for (const c of contacts.data || []) {
    const rol = c.custom_rol || '—'
    counts[rol] = (counts[rol] || 0) + 1
  }
  return Object.entries(counts).map(([rol, count]) => ({ rol, count }))
})

const contactRows = computed(() => {
  let data = contacts.data || []
  if (contactRolFilter.value)
    data = data.filter((c) => (c.custom_rol || '—') === contactRolFilter.value)
  return data.map(getContactRowObject)
})
const softwareRows = computed(() => [
  ...(software.data?.map(getSoftwareRowObject) || []),
  ...(procesos.data?.map(getProcesoRowObject) || []),
])

const { getFormattedCurrency } = getMeta('CRM Deal')

function getSoftwareRowObject(sw) {
  return {
    name: 'sw-' + sw.name,
    software_name: sw.software_name,
    tipo: __('Software'),
    dominio: sw.custom_dominio || '',
    modified: timestampCell(sw.modified),
  }
}

function getProcesoRowObject(p) {
  return {
    name: 'pt-' + p.name,
    software_name: p.nombre,
    tipo: __('Proceso / Tecnología'),
    dominio: '',
    modified: timestampCell(p.modified),
  }
}

const softwareColumns = [
  {
    label: __('Nombre'),
    key: 'software_name',
    width: '16rem',
  },
  {
    label: __('Tipo'),
    key: 'tipo',
    width: '11rem',
  },
  {
    label: __('Dominio'),
    key: 'dominio',
    width: '9rem',
  },
  {
    label: '',
    key: '_unlink',
    width: '3rem',
  },
]

async function unlinkSoftware(row) {
  try {
    if (String(row.name).startsWith('pt-')) {
      await call('frappe.client.set_value', {
        doctype: 'Procesos - Tecnologias',
        name: String(row.name).slice(3),
        fieldname: 'organization',
        value: '',
      })
      procesos.reload()
    } else {
      let doc = await call('frappe.client.get', {
        doctype: 'Software',
        name: String(row.name).slice(3),
      })
      doc.organizations = (doc.organizations || []).filter(
        (r) => r.organization !== props.organizationId,
      )
      await call('frappe.client.save', { doc: doc })
      software.reload()
    }
    toast.success(__('Desvinculado de la organización'))
  } catch (e) {
    toast.error(e.messages?.[0] || __('Error al desvincular'))
  }
}

function getDealRowObject(deal) {
  return {
    name: deal.name,
    organization: {
      label: deal.organization,
      logo: organization.doc?.organization_logo,
    },
    annual_revenue: getFormattedCurrency('annual_revenue', deal),
    status: {
      label: deal.status,
      color: getDealStatus(deal.status)?.color,
    },
    email: deal.email,
    mobile_no: deal.mobile_no,
    deal_owner: {
      label: deal.deal_owner && getUser(deal.deal_owner).full_name,
      ...(deal.deal_owner && getUser(deal.deal_owner)),
    },
    custom_numero_solaer: deal.custom_numero_solaer,
    custom_titulo: deal.custom_titulo,
    custom_producto: deal.custom_producto,
    contact: deal.contact,
    modified: timestampCell(deal.modified),
  }
}

function getLeadRowObject(lead) {
  return {
    name: lead.name,
    lead_name:
      lead.lead_name ||
      [lead.first_name, lead.last_name].filter(Boolean).join(' '),
    organization: {
      label: lead.organization,
      logo: organization.doc?.organization_logo,
    },
    status: {
      label: lead.status,
      color: getLeadStatus(lead.status)?.color,
    },
    email: lead.email,
    mobile_no: lead.mobile_no,
    lead_owner: {
      label: lead.lead_owner && getUser(lead.lead_owner).full_name,
      ...(lead.lead_owner && getUser(lead.lead_owner)),
    },
    modified: timestampCell(lead.modified),
  }
}

const leadColumns = [
  {
    label: __('Nombre'),
    key: 'lead_name',
    width: '12rem',
  },
  {
    label: __('Organización'),
    key: 'organization',
    width: '12rem',
  },
  {
    label: __('Status'),
    key: 'status',
    width: '11rem',
  },
  {
    label: __('Email'),
    key: 'email',
    width: '12rem',
  },
  {
    label: __('Teléfono'),
    key: 'mobile_no',
    width: '11rem',
  },
  {
    label: __('Responsable'),
    key: 'lead_owner',
    width: '11rem',
  },
]

function getContactRowObject(contact) {
  return {
    name: contact.name,
    full_name: {
      label: contact.full_name,
      image_label: contact.full_name,
      image: contact.image,
    },
    first_name: contact.first_name,
    last_name: (contact.last_name || '').toUpperCase(),
    custom_rol: contact.custom_rol,
    designation: contact.designation,
    custom_engagement: contact.custom_engagement,
    custom_relacion: contact.custom_relacion,
    email: contact.email_id,
    mobile_no: contact.mobile_no,
    company_name: {
      label: contact.company_name,
      logo: organization.doc?.organization_logo,
    },
    modified: timestampCell(contact.modified),
  }
}

const dealColumns = [
  {
    label: __('N° Solaer'),
    key: 'custom_numero_solaer',
    width: '5rem',
  },
  {
    label: __('Título'),
    key: 'custom_titulo',
    width: '12rem',
  },
  {
    label: __('Producto'),
    key: 'custom_producto',
    width: '10rem',
  },
  {
    label: __('Monto'),
    key: 'annual_revenue',
    align: 'right',
    width: '9rem',
  },
  {
    label: __('Status'),
    key: 'status',
    width: '10rem',
  },
  {
    label: __('Contacto primario'),
    key: 'contact',
    width: '12rem',
  },
  {
    label: __('Responsable comercial'),
    key: 'deal_owner',
    width: '11rem',
  },
]

const contactColumns = [
  {
    label: __('Nombre'),
    key: 'first_name',
    width: '9rem',
  },
  {
    label: __('Apellido'),
    key: 'last_name',
    width: '9rem',
  },
  {
    label: __('Rol'),
    key: 'custom_rol',
    width: '8rem',
  },
  {
    label: __('Designation'),
    key: 'designation',
    width: '10rem',
  },
  {
    label: __('Engagement'),
    key: 'custom_engagement',
    width: '9rem',
  },
  {
    label: __('Relación'),
    key: 'custom_relacion',
    width: '7rem',
  },
  {
    label: __('Email'),
    key: 'email',
    width: '12rem',
  },
  {
    label: __('Teléfono'),
    key: 'mobile_no',
    width: '11rem',
  },
]

const { showModal } = useDoctypeModal()

const showDealModal = ref(false)
const showContactModal = ref(false)

function createNew(tabLabel) {
  if (tabLabel === 'Deals') {
    showDealModal.value = true
  } else {
    showContactModal.value = true
  }
}

const showLinkSoftwareDialog = ref(false)
const linkSoftwareDoctype = ref('Software')

const linkSoftwareLabel = computed(() =>
  linkSoftwareDoctype.value === 'Software'
    ? 'Software'
    : 'Proceso / Tecnología',
)

const softwareCreateOptions = [
  {
    label: __('Software'),
    onClick: () =>
      showModal({
        doctype: 'Software',
        callbacks: {
          afterInsert: async (d) => {
            await call('frappe.client.insert', {
              doc: {
                doctype: 'Software Organization',
                parenttype: 'Software',
                parent: d.name,
                parentfield: 'organizations',
                organization: props.organizationId,
              },
            })
            software.reload()
          },
        },
      }),
  },
  {
    label: __('Proceso / Tecnología'),
    onClick: () =>
      showModal({
        doctype: 'Procesos - Tecnologias',
        defaults: { organization: props.organizationId },
        callbacks: { afterInsert: () => procesos.reload() },
      }),
  },
]

const softwareLinkOptions = [
  {
    label: __('Software'),
    onClick: () => openLinkSoftwareDialog('Software'),
  },
  {
    label: __('Proceso / Tecnología'),
    onClick: () => openLinkSoftwareDialog('Procesos - Tecnologias'),
  },
]

function openLinkSoftwareDialog(doctype) {
  linkSoftwareDoctype.value = doctype
  showLinkSoftwareDialog.value = true
}

async function linkSoftware(name) {
  if (!name) return
  showLinkSoftwareDialog.value = false
  try {
    if (linkSoftwareDoctype.value === 'Software') {
      if (software.data?.find((s) => s.name === name)) {
        toast.error(__('Ya está vinculado a esta organización'))
        return
      }
      await call('frappe.client.insert', {
        doc: {
          doctype: 'Software Organization',
          parenttype: 'Software',
          parent: name,
          parentfield: 'organizations',
          organization: props.organizationId,
        },
      })
      software.reload()
    } else {
      await call('frappe.client.set_value', {
        doctype: linkSoftwareDoctype.value,
        name: name,
        fieldname: 'organization',
        value: props.organizationId,
      })
      procesos.reload()
    }
    toast.success(__('Linked to organization'))
  } catch (e) {
    toast.error(e.messages?.[0] || __('Error linking document'))
  }
}

async function addExisting(tabLabel, name) {
  if (!name) return
  try {
    if (tabLabel === 'Deals') {
      await call('frappe.client.set_value', {
        doctype: 'CRM Deal',
        name: name,
        fieldname: 'organization',
        value: props.organizationId,
      })
      deals.reload()
    } else {
      await call('frappe.client.set_value', {
        doctype: 'Contact',
        name: name,
        fieldname: 'company_name',
        value: props.organizationId,
      })
      contacts.reload()
    }
    toast.success(__('Linked to organization'))
  } catch (e) {
    toast.error(e.messages?.[0] || __('Error linking document'))
  }
}

function showAddressModal(_address) {
  showModal({
    name: _address || null,
    doctype: 'Address',
    callbacks: {
      afterInsert: (d) => {
        capture('address_created')
        organization.doc.address = d.name
        organization.save.submit()
      },
    },
  })
}

// Setup custom actions from Form Scripts
watch(
  () => organization.doc,
  async (_doc) => {
    if (scripts.data?.length) {
      let s = await setupCustomizations(scripts.data, {
        doc: _doc,
        $dialog,
        $socket,
        router,
        toast,
        updateField: organization.setValue.submit,
        createToast: toast.create,
        deleteDoc: deleteOrganization,
        call,
      })
      organization._actions = s.actions || []
    }
  },
  { once: true },
)
</script>
