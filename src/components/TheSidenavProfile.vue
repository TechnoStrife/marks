<template>
    <li id="sidenav-profile" class="waves-effect">
        <div id="profile-icon" class="center-align">
            <img src="~src/assets/profile.png" alt="" class="circle">
        </div>
        <div id="user" class="white-text">
            <div id="user-name" class="truncate valign-wrapper">
                Иван Иванович
            </div>
            <div id="user-post" class="valign-wrapper">
                Директор
            </div>
        </div>
    </li>
</template>

<script>
export default {
    name: "TheSidenavProfile"
}
</script>

<style lang="scss">
#sidenav-profile {
    padding-top: 15px;
    padding-bottom: 15px;
    width: 100%;
    background: url(~src/assets/profile-background.png) no-repeat center center;
    background-size: cover;
    text-shadow: 1px 1px 1px #444;

    > #profile-icon {
        width: 86.5px;
        height: 64px;
        float: left;
    }

    > #user {
        width: 213px;
        padding: 0 12px;
        float: left;

        > #user-name {
            height: 32px;
            font-size: 1.2em;
            line-height: 32px;
        }

        > #user-post {
            height: 32px;
        }
    }
}
</style>
