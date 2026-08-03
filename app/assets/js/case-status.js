'use strict';

import { createApp } from 'vue'
import CaseStatus from "./vue/CaseStatus.vue";
import CaseDossierNr from "./vue/CaseDossierNr.vue";
import "./axios-csrf";

createApp(CaseStatus)
  .mount("#app")

if (!document.querySelector('[data-deny-dossier_nr]')){
  createApp(CaseDossierNr)
    .mount("#dossier_nr")
}