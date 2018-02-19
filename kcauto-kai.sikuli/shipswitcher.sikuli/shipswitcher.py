from sikuli import Region, Pattern
from math import ceil
from re import sub
from threading import Thread
from kca_globals import Globals
from nav import Nav
from util import Util


class ShipSwitcher(object):
    SHIPS_PER_PAGE = 10

    def __init__(self, config, stats, regions, fleets, combat):
        self.config = config
        self.stats = stats
        self.regions = regions
        self.kc_region = regions['game']
        self.fleets = fleets
        self.ship_count = 1
        self.ship_page_count = 1
        self.ship_last_page_count = 1
        self.current_shiplist_page = 1

        self.temp_ship_position_list = []
        self.temp_ship_position_dict = {}
        self.position_cache = {}

        x = self.kc_region.x
        y = self.kc_region.y
        self.module_regions = {
            'panels': [],
            'shiplist_class_col': Region(x + 350, y + 150, 200, 285),
        }
        for slot in range(0, 6):
            self.module_regions['panels'].append(Region(
                x + 121 + (352 * (slot % 2)),
                y + 135 + (113 * (slot / 2)),
                330, 110))

    def goto_fleetcomp(self):
        """Method to navigate to the fleet composition menu.
        """
        Nav.goto(self.regions, 'fleetcomp')
        self.current_shiplist_page = 1

    def check_need_to_switch(self):
        fleet = self.fleets[1]
        if fleet.damage_counts['repair'] > 0:
            # if ships are being repaired, attempt switch
            return True
        if fleet.get_damage_counts_at_threshold(
                self.config.combat['repair_limit']) > 0:
            # if ships are damaged at or above threshold, attempt switch
            return True
        if fleet.fatigue['medium'] > 0 or fleet.fatigue['high'] > 0:
            # ships are fatigued; brute force check for now
            # TODO: only True if fatigue check is part of config
            return True
        return False

    def ship_switch_logic(self):
        """Primary logic loop which goes through the 6 ship slots and switches
        ships as necessary. Only avilable for Fleet 1.
        """
        self._set_shiplist_counts()
        # loop through slots and switch ships as necessary
        for slot in range(0, 6):
            if slot not in self.config.ship_switcher:
                continue
            slot_config = self.config.ship_switcher[slot]
            if self._check_need_to_switch_ship(slot, slot_config['criteria']):
                Util.wait_and_click_and_wait(
                    self.module_regions['panels'][slot],
                    'shiplist_button.png',
                    self.regions['lower_right'],
                    'page_first.png')
                Util.rejigger_mouse(self.regions, 'top')
                if not self._resolve_replacement_ship(slot_config):
                    Util.check_and_click(
                        self.regions['top_submenu'], 'fleet_1_active.png')

        # check new fleet status
        fleet = self.fleets[1]
        damage_counts = fleet.check_damages(self.kc_region)
        if (fleet.get_damage_counts_at_threshold(
                    self.config.combat['repair_limit']) == 0 and
                damage_counts['repair'] == 0):
            # all ships in fleet pass checks: continue sortie
            fleet.set_next_combat_time()

    def _set_shiplist_counts(self):
        """Method that sets the ship-list related internal counts based on the
        number of ships in the port.
        """
        self.ship_count = self._get_ship_count()
        self.ship_page_count = int(
            ceil(self.ship_count / float(self.SHIPS_PER_PAGE)))
        self.ship_last_page_count = (
            self.ship_count % self.SHIPS_PER_PAGE
            if self.ship_count % self.SHIPS_PER_PAGE is not 0
            else self.SHIPS_PER_PAGE)

    def _get_ship_count(self):
        """Method that returns the number of ships in the port via the counter
        at the top of the screen when at home. Directly calls the
        read_ocr_number_text method then strips all non-number characters
        because Tesseract OCR has issues detecting short number of characters
        that are also white font on black backgrounds. Trick this by capturing
        more of the region than is needed (includes a bit of the bucket icon)
        then stripping out the superfluous/mis-recognized characters.

        Returns:
            int: number of ships in port
        """
        a = Util.read_ocr_number_text(
            self.regions['ship_counter'], 'shipcount_label.png', 'r', 48)
        return int(sub(r"\D", "", a))

    def _check_need_to_switch_ship(self, slot, criteria):
        """Method that checks whether or not the ship in the specified slot
        needs to be switched out based on the criteria.

        Args:
            slot (int): slot ID (0-base)
            criteria (dict): dictionary of criteria for the slot

        Returns:
            bool: True if the ship meets the criteria to be swapped out; False
                otherwise
        """
        panel_regions = self.module_regions['panels']
        if 'damage' in criteria:
            if panel_regions[slot].exists(
                    'ship_state_dmg_{}.png'.format(criteria['damage'])):
                return True
        if 'fatigue' in criteria:
            if panel_regions[slot].exists('__LOW_MORALE.png'):
                return True
        if 'sparkle' in criteria:
            print('checking for sparkle')
            if panel_regions[slot].exists('sparkle_indicator.png', 2):
                return True
        return False

    def _switch_shiplist_sorting(self, target):
        """Switches the shiplist sorting to the specified target mode.

        Args:
            target (str): the sorting to switch the shiplist to
        """
        while not self.regions['top_submenu'].exists(
                'shiplist_sort_{}.png'.format(target)):
            Util.check_and_click(
                self.regions['top_submenu'],
                'shiplist_sort_arrow.png',
                Globals.EXPAND['shiplist_sort'])

    def _change_shiplist_page(self, target):
        """Method that clicks on the arrow and page number navigation at the
        bottom of the ship list. 'first', 'prev', 'next', 'last' targets will
        click their respective arrow buttons, while an int target between 1 and
        5 (inclusive) will click the page number at that position at the bottom
        of the page (left to right).

        Args:
            target (str, int): specifies which navigation button to press
        """
        if target == 'first':
            Util.check_and_click(
                self.regions['lower'], 'page_first.png',
                Globals.EXPAND['arrow_navigation'])
        elif target == 'prev':
            Util.check_and_click(
                self.regions['lower'], 'page_prev.png',
                Globals.EXPAND['arrow_navigation'])
        elif target == 'next':
            Util.check_and_click(
                self.regions['lower'], 'page_next.png',
                Globals.EXPAND['arrow_navigation'])
        elif target == 'last':
            Util.check_and_click(
                self.regions['lower'], 'page_last.png',
                Globals.EXPAND['arrow_navigation'])
        elif 1 <= target <= 5:
            zero_target = target - 1
            x_start = 512 + (zero_target * 21) + (zero_target * 11)
            x_stop = x_start + 11
            y_start = 444
            y_stop = 452

            Util.click_coords(
                self.kc_region,
                Util.randint_gauss(x_start, x_stop),
                Util.randint_gauss(y_start, y_stop))

    def _navigate_to_shiplist_page(self, target_page):
        """Wrapper method that navigates the shiplist to the specified target
        page from the known current page. Uses _change_shiplist_page for
        navigation.

        Args:
            target_page (int): page to navigate to

        Raises:
            ValueError: invalid target_page specified
        """
        if target_page > self.ship_page_count:
            raise ValueError(
                "Invalid shiplist target page ({}) for number of known pages "
                "({}).".format(target_page, self.ship_page_count))

        current_page = self.current_shiplist_page
        # logic that fires off the series of _change_shiplist_page method calls
        # to navigate to the desired target page from the current page
        while target_page != current_page:
            page_delta = target_page - current_page
            if (target_page <= 5
                    and (current_page <= 3 or self.ship_page_count <= 5)):
                self._change_shiplist_page(target_page)
                current_page = target_page
            elif (current_page >= self.ship_page_count - 2
                    and target_page >= self.ship_page_count - 4):
                self._change_shiplist_page(
                    abs(self.ship_page_count - target_page - 5))
                current_page = target_page
            elif -3 < page_delta < 3:
                self._change_shiplist_page(3 + page_delta)
                current_page = current_page + page_delta
            elif page_delta <= - 3:
                if target_page <= 5:
                    self._change_shiplist_page('first')
                    current_page = 1
                else:
                    self._change_shiplist_page('prev')
                    current_page -= 5
            elif page_delta >= 3:
                if target_page > self.ship_page_count - 5:
                    self._change_shiplist_page('last')
                    current_page = self.ship_page_count
                else:
                    self._change_shiplist_page('next')
                    current_page += 5
        self.current_shiplist_page = current_page

    def _choose_ship_by_position(self, position):
        """Method that clicks the ship in the specified position in the ship
        list.

        Args:
            position (int): integer between 1 and 10 specifying the position
                that should be clicked on the ship list

        Raises:
            ValueError: invalid position specified
        """
        if not 1 <= position <= 10:
            raise ValueError(
                "Invalid position passed to _choose_ship_by_position: {}"
                .format(position))
        zero_position = position - 1
        # x start/stop do not change
        x_start = 389
        x_stop = 700
        # y start/stop change depending on specified position; region has width
        # of 326 pixels, height of 23 pixels, with a 5-pixel padding between
        # each nth position on the list
        y_start = 156 + (zero_position * 5) + (zero_position * 23)
        y_stop = y_start + 23

        Util.click_coords(
            self.kc_region,
            Util.randint_gauss(x_start, x_stop),
            Util.randint_gauss(y_start, y_stop))
        Util.kc_sleep(1)

    def _check_ship_availability(self, criteria):
        """Checks the chosen ship's returns its availability for switching.

        Args:
            criteria (dict): dictionary containing shipswitch criteria

        Returns:
            bool or str: True if the ship is available; False if it does not
                meet the criteria; 'conflict' if it meets the criteria but a
                ship of the same type is already in the fleet
        """
        # TODO: check against criteria
        if self.regions['upper_right'].exists('ship_state_dmg_heavy.png'):
            return False
        if Util.check_and_click(
                self.regions['lower_right'], 'shiplist_shipswitch_button.png'):
            return True
        else:
            return 'conflict'

    def _resolve_ship_page_and_position(self, reference, offset):
        """Given a start point (reference) and the offset, figure out the
        page and position based off the current number of ships.

        Args:
            reference (str): 'start' or 'end', indiciating where the offset
                begins from
            offset (int): n-position from reference

        Returns:
            int: page where the specified ship is
            list: list with one value indicating the position where the
                specified ship is on the specified page
        """
        if reference == 'start':
            start_offset = offset
        if reference == 'end':
            start_offset = self.ship_count - offset + 1
        page = int(ceil(start_offset / float(self.SHIPS_PER_PAGE)))
        position = (
            start_offset % self.SHIPS_PER_PAGE
            if start_offset % self.SHIPS_PER_PAGE is not 0
            else self.SHIPS_PER_PAGE)
        return (page, [position])

    def _filter_ships(self, matched_ships, ship_config):
        """Given a list of possible ship matches on the current ship list page,
        filter on the ship criteria and return a list of valid positions on the
        page.

        Args:
            matched_ships (list): list of regions, usually from a findAll
                wrapper
            ship_config (dict): dictionary of ship switch config

        Returns:
            list: list of positions of ships matching the criteria
        """
        ship_position_temp = []
        for ship in matched_ships:
            criteria_matched = True
            # create new region based on the match
            ship_row = ship.left(1).right(430)
            ship_row.setAutoWaitTimeout(0)  # speed
            # find numeric position based on the new region's y-position
            position = (ship_row.y - self.kc_region.y - 129) / 28

            # check against ship-specific criterias, if any
            if 'locked' in ship_config and criteria_matched:
                ship_locked = (
                    True if ship_row.exists('shiplist_lock.png') else False)
                criteria_matched = (
                    True if ship_config['locked'] == ship_locked else False)
            if 'ringed' in ship_config and criteria_matched:
                ship_ringed = (
                    True if ship_row.exists('shiplist_ring.png') else False)
                criteria_matched = (
                    True if ship_config['ringed'] == ship_ringed else False)
            if 'level' in ship_config and criteria_matched:
                level_area = Region(
                    ship_row.x + 160, ship_row.y, 50, ship_row.h)
                ship_level = Util.read_ocr_number_text(level_area)
                ship_level = 1 if not ship_level else ship_level
                if ship_config['level'][0] == '<':
                    criteria_matched = (
                        True if ship_level <= int(ship_config['level'][1:])
                        else False)
                if ship_config['level'][0] == '>':
                    criteria_matched = (
                        True if ship_level >= int(ship_config['level'][1:])
                        else False)

            if criteria_matched:
                ship_position_temp.append(position)
        ship_position_temp.sort()
        return ship_position_temp

    def _choose_and_check_availability_of_ship(self, position, criteria):
        """Select a ship in the ship list based on the specified position,
        and see if it available for switching in.

        Args:
            position (int): position in ship list
            criteria (dict): dictionary of criteria

        Returns:
            bool or str: result of _check_ship_availability() call
        """
        self._choose_ship_by_position(position)
        availability = self._check_ship_availability(criteria)
        if availability is True:
            return True
        Util.check_and_click(
            self.regions['lower_right'], 'page_first.png')
        return availability

    def _resolve_replacement_ship(self, slot_config):
        """Wrapper method to find and resolve a replacement ship.

        Args:
            slot_config (dict): dictionary containing the slot's config

        Returns:
            bool: True if a successful switch was made; False otherwise
        """
        # TODO: what happens when none of these specific methods dont' match???
        positions = []
        if slot_config['mode'] == 'position':
            return self._resolve_replacement_ship_by_position(slot_config)
        elif slot_config['mode'] == 'ship':
            return self._resolve_replacement_ship_by_ship(slot_config)
        elif slot_config['mode'] == 'class':
            return self._resolve_replacement_ship_by_class(slot_config)

    def _resolve_replacement_ship_by_position(self, slot_config):
        """Method that finds a resolves a replacement ship by position.

        Args:
            slot_config (dict): dictionary containing the slot's config

        Returns:
            bool: True if a successful switch was made; False otherwise
        """
        for ship in slot_config['ships']:
            self._switch_shiplist_sorting(ship['sort_order'])
            if 'offset_ref' in ship and 'offset' in ship:
                page, positions = self._resolve_ship_page_and_position(
                    ship['offset_ref'], ship['offset'])
                self._navigate_to_shiplist_page(page)
            # there should only be one returned position
            if self._choose_and_check_availability_of_ship(
                    positions[0], slot_config['criteria']) is True:
                return True
        return False

    def _resolve_replacement_ship_by_ship(self, slot_config):
        """Method that finds a resolves a replacement ship by specific ship.

        Args:
            slot_config (dict): dictionary containing the slot's config

        Returns:
            bool: True if a successful switch was made; False otherwise
        """
        ship_search_threads = []
        cache_override = True
        self.temp_ship_position_dict = {}
        self._switch_shiplist_sorting('class')

        # start search from cached position, if available
        if slot_config['slot'] in self.position_cache:
            self._navigate_to_shiplist_page(
                self.position_cache[slot_config['slot']])

        for ship in slot_config['ships']:
            ship_search_threads.append(Thread(
                target=self._match_shiplist_ships_func,
                args=('ship', ship['ship'], ship)))
        Util.multithreader(ship_search_threads)

        while (not self.temp_ship_position_list
                and self.current_shiplist_page < self.ship_page_count):
            Util.multithreader(ship_search_threads)

            if not self.temp_ship_position_dict:
                self._navigate_to_shiplist_page(self.current_shiplist_page + 1)
                continue

            if cache_override:
                # update cache on first encounter
                self._set_position_cache(slot_config['slot'])
                cache_override = False

            for ship_positions in self.temp_ship_position_dict:
                for position in ship_positions:
                    availability = self._choose_and_check_availability_of_ship(
                            position, slot_config['criteria'])
                    if availability is True:
                        return True
                    elif availability == 'dupe':
                        break

    def _resolve_replacement_ship_by_class(self, slot_config):
        """Method that finds a resolves a replacement ship by class.

        Args:
            slot_config (dict): dictionary containing the slot's config

        Returns:
            bool: True if a successful switch was made; False otherwise
        """
        ship_search_threads = []
        cache_override = True
        self.temp_ship_position_list = []
        self._switch_shiplist_sorting('class')

        # start search from cached position, if available
        if slot_config['slot'] in self.position_cache:
            self._navigate_to_shiplist_page(
                self.position_cache[slot_config['slot']])

        for ship in slot_config['ships']:
            ship_search_threads.append(Thread(
                target=self._match_shiplist_ships_func,
                args=('class', ship['class'], ship)))

        while (not self.temp_ship_position_list
                and self.current_shiplist_page < self.ship_page_count):
            Util.multithreader(ship_search_threads)

            if not self.temp_ship_position_list:
                self._navigate_to_shiplist_page(self.current_shiplist_page + 1)
                continue

            if cache_override:
                # update cache on first encounter
                self._set_position_cache(slot_config['slot'])
                cache_override = False

            self.temp_ship_position_list.sort()
            for position in self.temp_ship_position_list:
                if self._choose_and_check_availability_of_ship(
                        position, slot_config['criteria']) is True:
                    return True
            self.temp_ship_position_list = []
        return False

    def _match_shiplist_ships_func(self, mode, name, ship_config):
        """Child multithreaded method for finding matching classes and ships.

        Args:
            mode (str): specifies whether or not the search is for 'ship's or
                'class'es
            name (str): name of class or ship
            ship_config (dict): dictionary of ship criteria
        """
        img = (
            'shiplist_ship_{}.png'.format(name) if mode == 'ship'
            else 'shiplist_class_{}.png'.format(name))
        matched_ships = Util.findAll_wrapper(
            self.module_regions['shiplist_class_col'], img)

        ship_positions = self._filter_ships(matched_ships, ship_config)
        if mode == 'ship':
            if ship_positions:
                self.temp_ship_position_dict[name] = ship_positions
        elif mode == 'class':
            self.temp_ship_position_list.extend(ship_positions)

    def _set_position_cache(self, name):
        self.position_cache[name] = (
            self.current_shiplist_page - 1
            if self.current_shiplist_page - 1 > 0
            else 1)
