/** @odoo-module **/

import { useService } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";
import { browser } from "@web/core/browser/browser";
import { symmetricalDifference } from "@web/core/utils/arrays";

const { Component, hooks } = owl;
const { useState } = hooks;

export class SwitchJobMenu extends Component {
    setup() {
        this.jobService = useService("jobs");
        this.current_job = this.jobService.currentJob;
        this.state = useState({ jobsToToggle: [] });
    }
    logIntoJob(jobId) {
        browser.clearTimeout(this.toggleTimer);
        this.jobService.setJobs("loginto", jobId);
    }
    get selectedJobs() {
        return symmetricalDifference(
            this.jobService.allowedJobIds,
            this.state.jobsToToggle
        );
    }
}
SwitchJobMenu.template = "switch_jobs_menu.SwitchJobMenu";
SwitchJobMenu.toggleDelay = 1000;

export const systrayItem = {
    Component: SwitchJobMenu,
    isDisplayed(env) {
        const { availablejobs } = env.services.jobs;
        return Object.keys(availablejobs).length;
    },
};

registry.category("systray").add("SwitchJobMenu", systrayItem, { sequence: 2 });
