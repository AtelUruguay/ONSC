/** @odoo-module **/

import { browser } from "@web/core/browser/browser";
import { registry } from "@web/core/registry";
import { session } from "@web/session";

function parseJobIds(jibsFromHash) {
    const jibs = [];
    if (typeof jibsFromHash === "string") {
        jibs.push(...jibsFromHash.split(",").map(Number));
    } else if (typeof jibsFromHash === "number") {
        jibs.push(jibsFromHash);
    }
    return jibs;
}

function computeJobs(jibs) {
    const { jobs } = session;
    let allowedJobIds = jibs || [];
    const jobsFromSession = jobs.jobs;
    const notReallyAllowedJobs = allowedJobIds.filter(
        (id) => !(id in jobsFromSession)
    );

    if (!allowedJobIds.length || notReallyAllowedJobs.length) {
        allowedJobIds = [jobs.current_job];
    }
    else {
        allowedJobIds = [];
        for (let key in jobsFromSession) {
            allowedJobIds.push(jobsFromSession[key].id);
        }
    }
    return allowedJobIds;
}

export const jobService = {
        dependencies: ["orm", "user", "router", "cookie"],
    start(env, {orm, user, router, cookie }) {
        let jibs;
        if ("jibs" in router.current.hash) {
            jibs = parseJobIds(router.current.hash.jibs);
        } else if ("jibs" in cookie.current) {
            jibs = parseJobIds(cookie.current.jibs);
        }
        let allowedJobIds = computeJobs(jibs);

        const stringCIds = allowedJobIds.join(",");
        router.replaceState({ jibs: stringCIds }, { lock: true });
        cookie.setCookie("jibs", stringCIds);

        user.updateContext({ jobs: allowedJobIds });
        const availablejobs = session.jobs.jobs;
        return {
            availablejobs,
            get allowedJobIds() {
                return allowedJobIds.slice();
            },
            get currentJob() {
                return availablejobs[session.jobs.current_job];
            },
            async setJobs(mode, ...jobIds) {
                const jobId = jobIds[0];
                await orm.call("res.users", "change_job",  [user], {'jobId': jobId});
                var href = browser.location.origin;
                browser.setTimeout(() => browser.location.assign(href + '/web')); // history.pushState is a little async
            },
        };
    },
};

registry.category("services").add("jobs", jobService);