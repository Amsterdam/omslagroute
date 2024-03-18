<template>
    <div v-bind:class="setFormClass()">
        <div v-if="!enableUpdate && !initial" class="u-padding-top u-clearfix">
            <span>Dossier nr: <strong>{{ caseDossierNr }}</strong>&nbsp;</span>
            <a v-on:click="setEnableUpdate(true)" href="#" role="button" class="u-float-right u-underline--none screen-only" title="Wijzig dossiernummer">
                (wijzig)
            </a>
        </div>
        <div v-if="enableUpdate && !initial" class="case-number" data-targeted-content>
            <form v-on:submit.prevent="onSubmit">
                <div class="">
                    <label for="input_casenumber">Dossier nr</label>
                    <input v-model="caseDossierNr" type="text" placeholder="123456" id="input_casenumber" class="u-margin-right" />
                    <button v-on:click="updateCaseDossierNr()" type="submit" class="button button--primary screen-only">Bewaar</button>
                </div>
            </form>
        </div>
    </div>
</template>

<script>
import axios from "axios";

export default {
    name: "CaseDossierNr",
    data: () => ({
        caseDossierNr: null,
        caseId: null,
        enableUpdate: false,
        error: false,
        initial: true,
    }),
    created() {

    },
    beforeMount(){
        this.getInitialData();
        this.getCaseDossierNr(true);
    },
    methods: {
        onSubmit: function(){},
        setFormClass: function(){
            return this.error && 'error';
        },
        setEnableUpdate: function(enable){
            this.enableUpdate = enable;
        },
        getInitialData: function(){
            this.caseId = document.querySelector('[data-case-id]').dataset.caseId;
        },
        getCaseDossierNr: function () {
            axios.get(`/api/case-dossier-nr/${this.caseId}/`)
                .then((response) => {
                    this.caseDossierNr = response.data.wonen_dossier_nr;
                    this.enableUpdate = !this.caseDossierNr;
                    this.initial = false;
                })
                .catch((err) => {
                    console.log(err);
                })
        },
        updateCaseDossierNr: function () {
            axios.put(`/api/case-dossier-nr/${this.caseId}/`, {'wonen_dossier_nr': this.caseDossierNr})
                .then((response) => {
                    this.getCaseDossierNr();
                    this.error = !this.caseDossierNr;
                })
                .catch((err) => {
                    console.log(err);
                })
        },
    }
};
</script>