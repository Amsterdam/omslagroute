'use strict';

import { createApp } from 'vue'
import CaseDossierNr from "./vue/CaseDossierNr.vue";
import axios from "axios";

const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').getAttribute('value');

axios.defaults.headers.post['X-CSRFToken'] = csrfToken;
axios.defaults.headers.put['X-CSRFToken'] = csrfToken;
axios.defaults.headers.delete['X-CSRFToken'] = csrfToken;

createApp(CaseDossierNr)
  .mount("#dossier_nr")
