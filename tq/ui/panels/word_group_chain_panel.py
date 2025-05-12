def _send_to_geometric_transitions(self):
    """Send the current chain to the Geometric Transitions panel.

    This function creates a polygon in the Geometric Transitions panel where:
    - The number of sides equals the number of words in the chain
    - The vertex values are set to the values of each word in the chain
    """
    # Check if TQ module is available
    if not TQ_AVAILABLE:
        QMessageBox.warning(
            self,
            "Feature Unavailable",
            "The TQ module is not available in this installation.",
        )
        return

    # Check if a chain is selected
    current_item = self._chains_list.currentItem()
    if not current_item:
        QMessageBox.warning(
            self,
            "No Chain Selected",
            "Please select a chain to send to Geometric Transitions.",
        )
        return

    try:
        # Get the chain ID from the item's data
        chain_id = current_item.data(Qt.ItemDataRole.UserRole)
        chain = next((c for c in self._chains if c.chain_id == chain_id), None)

        if not chain:
            raise ValueError(f"Could not find chain with ID {chain_id}")

        # Get the service instance
        from tq.services.geometric_transition_service import GeometricTransitionService

        service = GeometricTransitionService.get_instance()

        # Get or create the window
        window = service.get_window()

        # Set up the polygon with the chain's values and labels
        values = [word.value for word in chain.words]
        labels = [word.text for word in chain.words]
        window.geometric_transition_panel.set_polygon_values(values, labels)

        # Open the window through the service
        service.open_window()

        logger.debug(f"Sent chain {chain_id} to geometric transitions window")

    except Exception as e:
        QMessageBox.warning(
            self,
            "Error",
            f"Could not send chain to Geometric Transitions: {str(e)}",
        )
        logger.error(f"Error sending chain to geometric transitions: {e}")
