'use strict';

import { createApp } from 'vue'
import CaseDossierNr from "./vue/CaseDossierNr.vue";
import "./axios-csrf";

createApp(CaseDossierNr)
  .mount("#dossier_nr")
